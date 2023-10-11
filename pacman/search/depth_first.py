from typing import List


class DFS:
    def dfs(self, labyrinth, path, used, src, dest) -> List:
        if src == dest:
            return path

        used.add(src)
        for to in labyrinth.edges[src]:
            if to not in used:
                path.append(to)
                result = self.dfs(labyrinth, path, used, to, dest)
                if result is not None:
                    return result
                path.pop(-1)
        used.pop()

    def apply(self, labyrinth, src, dest):
        return self.dfs(labyrinth, [], set(), src, dest)