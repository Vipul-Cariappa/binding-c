typedef struct RECT RECT;
typedef struct LinkedList LinkedList;
typedef struct Node Node;

struct RECT
{
    int x;
    int y;
};

struct Node
{
    int value;
    Node* next;
};


struct LinkedList
{
    Node* start;
    Node* end;
    int length;
};


int add(int x, int y);
int copy_int(int *destination, int *source);
char* concat(char* x, char* y);
double pi(int n);
RECT* get_rect(int x, int y);
RECT* rect_add(RECT* a, RECT* b);
int get_area(RECT* a);
int get_periment(RECT* a);
