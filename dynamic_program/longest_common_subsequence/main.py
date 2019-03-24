
# 计算最长递增子列，L[i]的值表示在原数列a[0:n]中以a[i]结尾的最长递增子列的长度
def LIS(a):
	L = [1 for _ in range(len(a))]
	L_str = [[a[0]]]
	for i in range(1,len(a)):
		L_str.append([])
		for j in range(i):
			if a[j] < a[i] and L[j] >= L[i]:
				L[i] = L[j] + 1
				L_str[i] = L_str[j][:]
				L_str[i].append(a[i])
	return L,L_str


def main():
	a = [0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15]
	L,L_str = LIS(a)
	print(L)
	print(L_str[4])

if __name__ == "__main__":
		main()