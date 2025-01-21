class Factorial{
    public static void main(String[] a){
        System.out.println(new Fac().ComputeFac(3));
    }
}
class Fac {
    public int ComputeFac(int num){
        {
            while (1 < num) {
                System.out.println(num);
                num = num - 1;
            }
        }
        return num;
    }
}