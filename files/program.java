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
        System.out.println(2);
	}
	
}

class A {
    A a;

    public int[] foo() {
        {}
        return 0;
    }
}

class B {
    C c;
}

class C {
    A a;
    B b;
}
	