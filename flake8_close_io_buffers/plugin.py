import ast
from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Optional, Tuple, Type


def set_parents(node: ast.AST, parent: Optional[ast.AST] = None) -> None:
    """
    Recursively attaches parent pointers to each AST node.
    """
    for child in ast.iter_child_nodes(node):
        setattr(child, "parent", node)
        set_parents(child, node)


@dataclass
class AssignedInfo:
    node: ast.Call
    closed: bool = False


class IOVisitor(ast.NodeVisitor):
    """
    Visits AST nodes to detect instantiations of io.BytesIO/io.StringIO and tracks
    whether they are safely closed (via a with-statement or an explicit .close() call).
    """
    assigned: Dict[str, AssignedInfo]
    issues: List[Tuple[int, int, str]]
    with_context: int

    def __init__(self) -> None:
        self.assigned = {}
        self.issues = []
        self.with_context = 0

    def visit_With(self, node: ast.With) -> None:
        # Process each item in the with-statement.
        for item in node.items:
            self.with_context += 1
            self.visit(item.context_expr)
            self.with_context -= 1

            # If the with-statement binds the context to a variable, mark it as closed.
            if item.optional_vars:
                for var in self._get_names(item.optional_vars):
                    if var in self.assigned:
                        self.assigned[var].closed = True

        # Continue visiting the body of the with-statement.
        for stmt in node.body:
            self.visit(stmt)

    def _node_contains(self, node: ast.AST, target: ast.AST) -> bool:
        """
        Returns True if 'target' is found within 'node' (by identity).
        """
        for child in ast.walk(node):
            if child is target:
                return True
        return False

    def _find_assigned_names(self, call: ast.Call) -> List[str]:
        """
        Walks up the parent chain to see if this call is part of an assignment.
        If the assigned value is a tuple or list, it finds the correct index and returns
        the corresponding target names.
        """
        original_call: ast.Call = call
        cur: ast.AST = call
        assign_node: Optional[ast.Assign] = None

        # Climb up until we find an Assign node.
        while True:
            parent = getattr(cur, "parent", None)
            if parent is None:
                break
            if isinstance(parent, ast.Assign):
                assign_node = parent
                break
            cur = parent

        if assign_node is None:
            return []

        # If the assign value is a tuple or list, try to match the call to the correct element.
        if isinstance(assign_node.value, (ast.Tuple, ast.List)):
            index: Optional[int] = None
            for idx, elt in enumerate(assign_node.value.elts):
                if self._node_contains(elt, original_call):
                    index = idx
                    break
            if index is not None:
                names: List[str] = []
                for target in assign_node.targets:
                    if isinstance(target, (ast.Tuple, ast.List)) and len(target.elts) > index:
                        names.extend(self._get_names(target.elts[index]))
                    else:
                        names.extend(self._get_names(target))
                return names

        # Fallback: return all names from the targets.
        names: List[str] = []
        for target in assign_node.targets:
            names.extend(self._get_names(target))
        return names

    def visit_Call(self, node: ast.Call) -> None:
        # Look for instantiations of io.BytesIO or io.StringIO.
        if isinstance(node.func, ast.Attribute):
            func_attr: ast.Attribute = node.func
            if (
                isinstance(func_attr.value, ast.Name)
                and func_attr.value.id == "io"
                and func_attr.attr in {"BytesIO", "StringIO"}
            ):
                if self.with_context > 0:
                    # Instantiation inside a with-statement header is considered safe.
                    pass
                else:
                    names: List[str] = self._find_assigned_names(node)
                    if names:
                        for name in names:
                            self.assigned[name] = AssignedInfo(node=node, closed=False)
                    else:
                        self.issues.append(
                            (
                                node.lineno,
                                node.col_offset,
                                "IO100 unclosed IO object instantiation not assigned to a variable",
                            )
                        )
        # Look for calls to .close() to mark variables as closed.
        if isinstance(node.func, ast.Attribute) and node.func.attr == "close":
            if isinstance(node.func.value, ast.Name):
                var_name: str = node.func.value.id
                if var_name in self.assigned:
                    self.assigned[var_name].closed = True
        self.generic_visit(node)

    def _get_names(self, node: ast.AST) -> List[str]:
        """
        Recursively collects variable names from an assignment target.
        """
        if isinstance(node, ast.Name):
            return [node.id]
        elif isinstance(node, (ast.Tuple, ast.List)):
            names: List[str] = []
            for elt in node.elts:
                names.extend(self._get_names(elt))
            return names
        return []


class UnclosedIOChecker:
    """
    Flake8 plugin that detects io.BytesIO/io.StringIO instantiations that are not closed.

    Error code:
      IO100 unclosed IO object <var> is not closed
    """
    name: str = "flake8-unclosed-io"
    version: str = "0.1.0"

    def __init__(self, tree: ast.AST, filename: str) -> None:
        self.tree = tree
        self.filename = filename

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        """
        Yields a tuple (line, col, message, type) for each detected error.
        """
        set_parents(self.tree)
        visitor: IOVisitor = IOVisitor()
        visitor.visit(self.tree)

        # Report errors for assigned IO objects that were not closed.
        for var, info in visitor.assigned.items():
            if not info.closed:
                yield (
                    info.node.lineno,
                    info.node.col_offset,
                    f"IO100 unclosed IO object '{var}' is not closed",
                    type(self),
                )

        # Report errors for IO instantiations that were not assigned.
        for lineno, col_offset, msg in visitor.issues:
            yield (lineno, col_offset, msg, type(self))
