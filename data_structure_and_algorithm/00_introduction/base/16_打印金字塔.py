"""

     *        
    ***       
   *****
  *******
 *********

"""
n = int(input(f"请输入一个数字:"))

for x in range (1, n+1):
     for z in range (1, n-x+1):
          print(" ", end="")
     for y in range (0, 2*x-1):
          print("*", end="")
     print("\n")