class BitSet:
    def __init__(self, size):
        self.size = size
        self.bitset = [0] * (size // 32 + 1)

    def __getitem__(self, index):
        return self.bitset[index // 32] & (1 << (index % 32)) != 0

    def __setitem__(self, index, value):
        if value:
            self.bitset[index // 32] |= 1 << (index % 32)
        else:
            self.bitset[index // 32] &= ~(1 << (index % 32))

    def __str__(self):
        return ''.join(str(int(self[i])) for i in range(self.size))

    def __repr__(self):
        return f"BitSet({self.size})"

    def __eq__(self, other):
        return self.bitset == other.bitset

    def __hash__(self):
        return hash(tuple(self.bitset))

    def __len__(self):
        return self.size

    def __bool__(self):
        return any(self.bitset)

    def __invert__(self):
        result = BitSet(self.size)
        for i in range(len(self.bitset)):
            result.bitset[i] = ~self.bitset[i]
        return result

    def __and__(self, other):
        result = BitSet(self.size)
        for i in range(len(self.bitset)):
            result.bitset[i] = self.bitset[i] & other.bitset[i]
        return result

    def __or__(self, other):
        result = BitSet(self.size)
        for i in range(len(self.bitset)):
            result.bitset[i] = self.bitset[i] | other.bitset[i]
        return result

    def __invert__(self):
        result = BitSet(self.size)
        for i in range(len(self.bitset)):
            result.bitset[i] = ~self.bitset[i]
        return result

    def __sub__(self, other):
        return self & ~other

    def __add__(self, other):
        return self | other

    def __mul__(self, other):
        return self & other

    def __contains__(self, item):
        return self[item]

    def __iter__(self):
        for i in range(self.size):
            yield self[i]

    def copy(self):
        result = BitSet(self.size)
        result.bitset = self.bitset.copy()
        return result
