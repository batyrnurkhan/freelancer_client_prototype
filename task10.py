t = [6, 4, 2, 2, 3, 3, 2, 4, 2, 3, 3, 4]
K = [
    [],
    [0],
    [0],
    [0],
    [1],
    [2],
    [3],
    [4, 5, 6],
    [4, 5, 6],
    [8, 6],
    [3],
    [7, 9, 10]
]
Kp = [
    [3, 2, 1],
    [4],
    [5],
    [10, 6],
    [8, 7],
    [8, 7],
    [9, 8, 7],
    [11],
    [9],
    [11],
    [11],
    []
]
trk = [0] * 12
trn = [0] * 12
tpk = [0] * 12
tpn = [0] * 12
r = [0] * 12

for i in range(len(t)):
    trk[i] = t[i]
    l = 0
    tmpi = trk[i]
    for j in K[i]:
        tmp = trk[i]
        if l > 0:
            if trk[j] > t[j]:
                tmp = tmpi + trk[j]
            else:
                tmp = tmpi + t[j]
            trk[i] = max(tmp, trk[i])
        else:
            trk[i] += trk[j] if trk[j] > t[j] else t[j]
        l += 1

for i in range(len(t)):
    trn[i] = trk[i] - t[i] + 1

tpk[-1] = 22
for i in range(11, -1, -1):
    tpk[i] = min(tpk[i], 999999999)
    tmpi = tpk[i]
    for j in Kp[i]:
        tpk[i] = min(tpk[j] - t[j], tmpi)

for i in range(len(t)):
    tpn[i] = tpk[i] - t[i] + 1
    r[i] = tpk[i] - trk[i]

print("i | t(i) | K(i) | trn(i) | trk(i) | tpn(i) | tpk(i) | r(i)")
for i in range(len(t)):
    print(f"{i} | {t[i]} | {K[i]} | {trn[i]} | {trk[i]} | {tpn[i]} | {tpk[i]} | {r[i]}")

print(f"Results:\nt(i)     {t}\nK(i)     {K}\nt(rn, i) {trn}\nt(rk, i) {trk}\nt(pn, i) {tpn}\nt(pk, i) {tpk}\nr(i)     {r}")
