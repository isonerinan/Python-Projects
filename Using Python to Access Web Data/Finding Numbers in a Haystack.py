import re

## sampleSum = open("regex_sum_42.txt") ## sum is 445833
sumFile = open("regex_sum_1389548.txt")
sum = 0

##for line in sampleSum:
for line in sumFile:
    sumList = re.findall("[0-9]+", line)

    for num in sumList:
        sum += int(num)

print(sum)