from pathlib import Path

try:
    from ..schema import artifact_ref
except ImportError:
    from schema import artifact_ref


class DocumentManager:
    def collect(self, paths, parser):
        unique = []
        seen = set()
        for path in paths:
            resolved = Path(path).resolve()
            if resolved.is_file() and resolved not in seen:
                seen.add(resolved)
                unique.append(artifact_ref(resolved, parser))
        return unique

