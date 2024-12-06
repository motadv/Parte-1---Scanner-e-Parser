public class HelloWorld {

    public static void main(String[] args) {
        // Este é um comentário de linha única
        int a = 5; // Outro comentário

        /* Comentário de bloco
           que se estende por várias linhas */
        int b = 10; /* Comentário no meio da linha */ int c = 15;

        // Comentário antes de uma declaração
        int sum = a + b + c; // Comentário após uma declaração

        // Comentário aleatório
        if (a > b) {
            System /* comentário */ . /* comentário */ out /* comentário */ . /* comentário */ println(a); // Comentário dentro de um bloco
        } else {
            System /* comentário */ . /* comentário */ out /* comentário */ . /* comentário */ println(b);
        }

        // Comentário com espaços estranhos
        for (int i = 0; i < 5; i = i + 1) {
            System /* comentário */ . /* comentário */ out /* comentário */ . /* comentário */ println(i);
        }

        // Comentário final
        int /* comentário */ x /* comentário */ = /* comentário */ 10 /* comentário */ ; // Atribuição com comentário
        int /* comentário */ y /* comentário */ = /* comentário */ 20 /* comentário */ ; // Atribuição com comentário
        int total = x /* comentário */ + /* comentário */ y; // Soma com comentário
    }
}