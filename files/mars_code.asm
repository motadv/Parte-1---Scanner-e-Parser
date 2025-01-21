.main:
li $v0, 9
li $a0, 4
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
addiu $sp, $sp, 8
# Saved the return address
sw $ra, 0($sp)
addiu $sp, $sp, -4
while_1:
# Loading constant 1 into $a0
li $a0, 1
sw $a0, 0($sp)
addiu $sp, $sp, -4
# Lookin at the value of num
lw $a0, -4($fp)
lw $t0, 4($sp)
addiu $sp, $sp, 4
slt $a0, $t0, $a0
beq $a0, $zero, end_while_1
# Lookin at the value of num
lw $a0, -4($fp)
li $v0, 1
syscall
# Lookin at the value of num
lw $a0, -4($fp)
sw $a0, 0($sp)
addiu $sp, $sp, -4
# Loading constant 1 into $a0
li $a0, 1
lw $t0, 4($sp)
addiu $sp, $sp, 4
sub $a0, $t0, $a0
# Value to input is in $a0
sw $a0, -4($fp)
b while_1
end_while_1:
# Saving the return value
# Lookin at the value of num
lw $a0, -4($fp)
# Loaded the return address
lw $ra, 4($sp)
addiu $sp, $sp, 4
# Restoring the frame pointer
addiu $sp, $sp, -8
jr $ra
