// class Factorial{
//     public static void main(String[] a){
//         System.out.println(new Fac().ComputeFac(10));
//     }
// }
// class Fac {
//     int num_extra;

//     public int ComputeFac(int num){
//         int num_aux;
//         {
//             if (num < 1) {
//                 num_aux = 1;
//             }
//             else {
//                 num_aux = num * (this.ComputeFac(num-1));
//             }
//         }
//         return num_aux ;
//     }
// }

class Main
{
	public static void main(String[] args) {
        System.out.println(1 + 2 + 4 + 8 + 16);
	}
	
}

class A {
    int num1;
    int num2;
    int num3;
    int result;

    public int foo() {
        {
            num1 = 1 * 1 * 1 * 1 * 1;
            result = num1;
        }
        return result;
    }
}


class B {
    A a;
    int returnVal;



    public int foo() {
        {
            returnVal = 1 + 5 + 10 + 15 + 20;
        }
        return returnVal;
    }
}

class C {
    public int foo() {
        {}
        return 0;
    }
}