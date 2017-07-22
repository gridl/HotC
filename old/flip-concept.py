
# 25 wide, and take the longest height

# 0 - standing
# 1 - punch
# 2 - block
# 3 - throw

def r(s, a, b):
    return s.replace(a, '%temp%').replace(b, a).replace('%temp%', b)

with open('batman-3.txt') as f:
    santa = f.read().splitlines()
with open('batman.txt') as f:
    batman = f.read().splitlines()

for i in range(18):
    right = santa[i][::-1]
    right = r(right, '/', '\\')
    right = r(right, '(', ')')
    right = r(right, '[', ']')
    right = r(right, '{', '}')
    right = r(right, '<', '>')

    # print '{:25}{}{:>25}'.format(batman[i], ' '*5, right)
    print '{:>25}'.format(right)
