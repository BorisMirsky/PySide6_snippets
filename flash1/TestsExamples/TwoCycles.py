

a = 10
b = ['q', 'w', 'e', 'r', 't']
result = []

#for i in range(0,a,1):
counter=0
for j in b:
    for i in range(0,a,1):
        print(counter, j * 10)
        counter += 1

#for i in b:
#    result.append(i * 10)

#print(result)