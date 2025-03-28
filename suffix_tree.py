class Node:
    def __init__(self, key=None, value=None, parent=None, childs=None):
        if childs is None:
            childs = []
        self.key = key
        self.value = value
        self.parent = parent
        self.childs = childs

    def is_root(self):
        return not self.parent

    def is_leaf(self):
        return not self.childs


class SuffixTree:
    def __init__(self):
        self.root = Node()
        self.size = 1

    def get(self, key):
        if self.root:
            result = self._get(key, self.root)
            if result:
                return result.value
            else:
                return None
        else:
            return None

    def _get(self, key, current_node):
        if current_node is None:
            return None
        if key < current_node.key:
            return self._get(key, current_node.left_child)
        elif key > current_node.key:
            return self._get(key, current_node.right_child)
        return current_node

    def put(self, key, value=None):
            self.size += 1
            self._put(key, self.root)


    def _put(self, key, current_node):
        if not current_node.childs:
            node = Node(key=key, parent=current_node)
            current_node.childs.append(node)
            return
        flag = False
        for ch in current_node.childs:
            if key == ch.key:
                return
            elif key.startswith(ch.key):
                if not ch.childs:
                    ch.key = key
                else:
                    self._put(key[len(ch.key):], ch)
                return
            elif ch.key.startswith(key):
                return
            else:
                i =  self.same_beginnig(ch.key, key)
                if i != 0:
                    new_node = Node(key=ch.key[i:], parent=ch, childs=ch.childs)
                    ch.key = ch.key[:i]
                    ch.childs = [new_node]
                    node = Node(key=key[i:], parent=ch)
                    ch.childs.append(node)
                    return
        node = Node(key=key, parent=current_node)
        self.root.childs.append(node)

    def same_beginnig(self, key1, key2):
        n = min(len(key1), len(key2))
        for i in range(n):
            if key1[i] != key2[i]:
                return i
        return 0


    def get_height(self):
        if not self.root:
            return 0
        return self._get_height(self.root, 0)

    def _get_height(self, node, height):
        if not node:
            return height - 1
        height += 1
        return max(self._get_height(node.left_child, height),
                   self._get_height(node.right_child, height))

    def depth_traversal(self, mode="LNR"):
        if not self.root:
            return []
        return self._depth_traversal(self.root, [], mode)

    def _depth_traversal(self, node, keys, mode):
        if node:
            if mode.upper() == "NLR":
                keys.append(node.key)
                self._depth_traversal(node.left_child, keys, mode)
                self._depth_traversal(node.right_child, keys, mode)
            elif mode.upper() == "LNR":
                self._depth_traversal(node.left_child, keys, mode)
                keys.append(node.key)
                self._depth_traversal(node.right_child, keys, mode)
            elif mode.upper() == "LRN":
                self._depth_traversal(node.left_child, keys, mode)
                self._depth_traversal(node.right_child, keys, mode)
                keys.append(node.key)
        return keys

    def breadth_traversal(self):
        bst_as_list_of_keys = []
        level = [self.root]
        len_level = 1
        while len(level) != 0:
            level_keys = []
            for i in range(len_level):
                level_keys.append(level[i].key)
                level.extend(level[i].childs)
            bst_as_list_of_keys.append(level_keys)
            level = level[len_level:]
            len_level = len(level)
        return bst_as_list_of_keys

    def _left_rotation(self, rot_root):
        new_root = rot_root.right_child
        rot_root.right_child = new_root.left_child
        if new_root.left_child:
            new_root.left_child.parent = rot_root
        new_root.parent = rot_root.parent
        if new_root.is_root():
            self.root = new_root
        else:
            if rot_root.is_left_child():
                rot_root.parent.left_child = new_root
            else:
                rot_root.parent.right_child = new_root
        new_root.left_child = rot_root
        rot_root.parent = new_root

    def _right_rotation(self, rot_root):
        new_root = rot_root.left_child
        rot_root.right_child = new_root.right_child
        if new_root.right_child:
            new_root.right_child.parent = rot_root
        new_root.parent = rot_root.parent
        if new_root.is_root():
            self.root = new_root
        else:
            if rot_root.is_left_child():
                rot_root.parent.left_child = new_root
            else:
                rot_root.parent.right_child = new_root
        new_root.right_child = rot_root
        rot_root.parent = new_root


st = SuffixTree()
s = "banana$"
n = len(s)
for i in range(1, n + 1):
    for j in range(i):
        st.put(s[j:i])
    print(st.breadth_traversal())
print(st.breadth_traversal())