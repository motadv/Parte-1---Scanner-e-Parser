.main:
li $v0, 9
li $a0, 8
syscall
sw $v0, 0($v0)
move $a0, $v0
sw $fp, 0($sp)
addiu $sp, $sp, -4
move $fp, $sp
# Saving object address
sw $a0, 0($fp)
addiu $fp $fp -4
# Loading constant 3 into $a0
li $a0, 3
# Saving a new parameter
sw $a0, 0($fp)
addiu $fp, $fp, -4
jal Fac_ComputeFac
lw $fp, 4($sp)
addiu $sp, $sp, 4
li $v0, 1
syscall
li $v0, 10
syscall
Fac_ComputeFac:
move $fp, $sp
addiu $sp, $sp, 12
# Saved the return address
sw $ra, 0($sp)
addiu $sp, $sp, -4
sw $zero, -8($fp)
# Lookin at the value of num
lw $a0, -4($fp)
sw $a0, 0($sp)
addiu $sp, $sp, -4
# Loading constant 1 into $a0
li $a0, 1
lw $t0, 4($sp)
addiu $sp, $sp, 4
slt $a0, $t0, $a0
beq $a0, $zero, else_1
if_1:
# Loading constant 1 into $a0
li $a0, 1
# Value to input is in $a0
sw $a0, -8($fp)
b end_if_1
else_1:
# Lookin at the value of num
lw $a0, -4($fp)
sw $a0, 0($sp)
addiu $sp, $sp, -4
# Lookin at the value of this
lw $a0, 0($fp)
addi $a0, $a0, 0
lw $a0, 0($a0)
lw $t0, 4($sp)
addiu $sp, $sp, 4
mul $a0, $a0, $t0
# Value to input is in $a0
sw $a0, -8($fp)
end_if_1:
# Saving the return value
# Lookin at the value of num_aux
lw $a0, -8($fp)
# Loaded the return address
lw $ra, 4($sp)
addiu $sp, $sp, 4
# Restoring the frame pointer
addiu $sp, $sp, -12
jr $ra
