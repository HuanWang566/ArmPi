#include <stdio.h>
#include <fcntl.h>      //open函数的定义
#include <unistd.h>     //close函数的定义
#include <sys/types.h>  
#include <sys/mman.h>   //mmap函数的定义
#include <errno.h>      //errno的定义
#include <string.h>
#include <stdint.h>     //uint8_t、uint32_t等类型的定义
#include <unistd.h>     //sleep函数的定义
#include <termios.h>
//#include <curses.h>
 
//BCM2837外设的物理地址
#define PERIPHERALS_PHY_BASE 0x3F000000
//外设物理地址的数量
#define PERIPHERALS_ADDR_SIZE 0x01000000
 
//引脚高电平
#define HIGH 0x01
//引脚低电平
#define LOW 0x00
 
int memfd;
                   
volatile uint32_t* bcm2837_peripherals_base;
volatile uint32_t* bcm2837_gpio_base;

struct termios opt;
 
//定义寄存器地址
volatile uint32_t* GPFSEL0;
volatile uint32_t* GPFSEL1;
volatile uint32_t* GPFSEL2;
volatile uint32_t* GPFSEL3;
volatile uint32_t* GPSET0;
volatile uint32_t* GPCLR0;
 
 
//将物理地址映射到用户进程的虚拟地址
int8_t paddr2vaddr();
//设置引脚3为输出功能
void pin3_select_output();
//控制引脚3的电平
void pin31_ctrl(uint8_t level);
//往地址addr写入值value
void write_addr(volatile uint32_t* addr, uint32_t value);
//读取地址addr的值
uint32_t read_addr(volatile uint32_t* addr);

static   struct  termios oldt;

void  restore_terminal_settings( void )
{
     // Apply saved settings
    tcsetattr( 0 , TCSANOW,  & oldt); 
}

void  disable_terminal_return( void )
{
     struct  termios newt;
    
     // save terminal settings
    tcgetattr( 0 ,  & oldt); 
     // init new settings
    newt  =  oldt;  
     // change settings
    newt.c_lflag  &=   ~ (ICANON  |  ECHO);
     // apply settings
    tcsetattr( 0 , TCSANOW,  & newt);
    
     // make sure settings will be restored when program ends
    atexit(restore_terminal_settings);
}

void portInit()
{
    volatile uint32_t* reg;
	uint32_t value;

	// set GPIO17/GPIO27 as input
	value = read_addr(GPFSEL1);
    //1111 1111 0001 1111 1111 1111 1111 1111 -> 0xFF1FFFFF
    //0000 0000 0010 0000 0000 0000 0000 1000 -> 0x00200000
    value = (value & 0xFF1FFFFF) | 0x00200000;
    write_addr(GPFSEL1, value);
 
    reg = GPCLR0;
    value = read_addr(reg);
    //1111 1111 1111 1101 1111 1111 1111 1111 -> 0xFFFDFFFF
    //0000 0000 0000 0010 0000 0000 0000 0000 -> 0x00020000
    value = (value & 0xFFFDFFFF) | 0x00020000;
    write_addr(reg, value);	

	value = read_addr(GPFSEL2);
    //1111 1111 0001 1111 1111 1111 1111 1111 -> 0xFF1FFFFF
    //0000 0000 0010 0000 0000 0000 0000 1000 -> 0x00200000
    value = (value & 0xFF1FFFFF) | 0x00200000;
    write_addr(GPFSEL2, value);

	reg = GPSET0;
    value = read_addr(reg);
    //1111 0111 1111 1111 1111 1111 1111 1111 -> 0xF7FFFFFF
    //0000 1000 0000 0000 0000 0000 0000 0000 -> 0x08000000
    value = (value & 0xF7FFFFFF) | 0x08000000;
    write_addr(reg, value);	
}

void init(int fd)
{
    //物理地址映射到虚拟地址
    if(!paddr2vaddr())
    {
        printf("map error\n");
    }

    tcgetattr(fd, &opt);
    cfsetispeed(&opt, B115200);
    cfsetospeed(&opt, B115200);
    opt.c_cflag |= (CLOCAL | CREAD);
    opt.c_cflag &= ~CSIZE;
    opt.c_cflag |= CS8;
    opt.c_cflag &= ~PARENB;
    opt.c_cc[VTIME] = 0;
    opt.c_cc[VMIN] = 0;
    opt.c_oflag = ~ (OPOST | ONLCR | OCRNL);
    tcflush(fd, TCIFLUSH);
    tcsetattr(fd, TCSANOW, &opt);

    //pin31的功能选择为输出
    //pin31_select_output();

	//set GPIO17/GPIO27
	portInit();

    //pin3_ctrl(LOW);
}

void portWrite()
{
    volatile uint32_t* reg;
	uint32_t value;

	// set GPIO17 0/GPIO27 1

	reg = GPSET0;
    value = read_addr(reg);
    //1111 0111 1111 1111 1111 1111 1111 1111 -> 0xF7FFFFFF
    //0000 1000 0000 0000 0000 0000 0000 0000 -> 0x08000000
    value = (value & 0xF7FFFFFF) | 0x08000000;
    write_addr(reg, value);	

    reg = GPCLR0;
    value = read_addr(reg);
    //1111 1111 1111 1101 1111 1111 1111 1111 -> 0xFFFDFFFF
    //0000 0000 0000 0010 0000 0000 0000 0000 -> 0x00020000
    value = (value & 0xFFFDFFFF) | 0x00020000;
    write_addr(reg, value);	
}

int checksum(char *buf, int n)
{
	int i;
	int sum = 0;

	for (i = 0; i < n; i++) {
		sum+=buf[i];
	}
	sum = sum - 85 - 85;
	sum = ~sum;
	return sum & 0xff;
}

void setBusServoPulse(int id, int pos, int time,int fd)
{
    printf("setBusServoPulse\n");
    portWrite();
	int i = 0;
	char buf[10];
	int n = 10;
	buf[0] = 85;
	buf[1] = 85;
	buf[2] = id;
	buf[3] = 7;
	buf[4] = 1;
	buf[5] = (0xff & pos);
	buf[6] = (0xff & (pos >> 8));
	buf[7] = (0xff & time);
	buf[8] = (0xff & (time >> 8));
	buf[9] = checksum(buf, 9);
	for (i = 0; i < n; i++) {
		printf("%x\n", buf[i]);
	}
    write(fd, buf, 10);
}
 
int main()
{
    int fd = open("/dev/ttyAMA0", O_RDWR|O_NOCTTY|O_NDELAY);
	init(fd);
    char input;

    //disable_terminal_return();
	while(1) {
    //     switch(input)
    //     {
    //     case 'q':
    //         setBusServoPulse(1, 200, 500, fd);
    //         break;
    //     case 'e':
    //         setBusServoPulse(1, 500, 500, fd);
    //         break;
    //     case 'w':
    //         setBusServoPulse(3, 500, 500, fd);
    //         break;
    //     case 's':
    //         setBusServoPulse(3, 200, 500, fd);
    //         break;
    //     case 'a':
    //         setBusServoPulse(2, 200, 500, fd);
    //         break;
    //     case 'd':
    //         setBusServoPulse(2, 500, 500, fd);
    //         break;
    //     case 'i':
    //         setBusServoPulse(4, 500, 500, fd);
    //         break;
    //     case 'k':
    //         setBusServoPulse(4, 200, 500, fd);
    //         break;
    //     case 'u':
    //         setBusServoPulse(5, 200, 500, fd);
    //         break;
    //     case 'o':
    //         setBusServoPulse(5, 500, 500, fd);
    //         break;
    //     case 'j':
    //         setBusServoPulse(6, 200, 500, fd);
    //         break;
    //     case 'l':
    //         setBusServoPulse(6, 500, 500, fd);
    //         break;
    //     }
    //     sleep(1);
    // for (int i = 10; i < 999; i++) {
    //     setBusServoPulse(i, 100, 500, fd);
    //     sleep(1);
    // }

		setBusServoPulse(3, 500, 500, fd);
    	sleep(1);
		setBusServoPulse(3, 550, 500, fd);
    	sleep(1);
		setBusServoPulse(2, 300, 500, fd);
    	sleep(1);

		setBusServoPulse(2, 700, 700, fd);
    	sleep(1);


		setBusServoPulse(2, 500, 500, fd);
    	sleep(1);

		setBusServoPulse(1, 0, 500, fd);
        sleep(1);
		setBusServoPulse(1, 1000, 700, fd);
        sleep(1);
		setBusServoPulse(1, 400, 500, fd);
    	sleep(1);

		setBusServoPulse(4, 850, 700, fd);
        sleep(1);
		setBusServoPulse(4, 1000, 500, fd);
    	sleep(1);

		setBusServoPulse(5, 600, 500, fd);
        sleep(1);
		setBusServoPulse(5, 750, 500, fd);
    	sleep(1);

		setBusServoPulse(6, 200, 500, fd);
        sleep(1);
		setBusServoPulse(6, 800, 700, fd);
        sleep(1);
		setBusServoPulse(6, 500, 500, fd);
    	sleep(1);
	}
    close(fd);
}
 
int8_t paddr2vaddr()
{
    if( (memfd = open("/dev/mem", O_RDWR | O_SYNC))  >= 0 )
    {
    	//“/dev/mem”内是物理地址的映像
    	//通过mmap函数将物理地址映射为用户进程的虚拟地址
        bcm2837_peripherals_base = mmap(NULL, PERIPHERALS_ADDR_SIZE, (PROT_READ | PROT_WRITE),
                                        MAP_SHARED, memfd, (off_t)PERIPHERALS_PHY_BASE);
 
        if(bcm2837_peripherals_base == MAP_FAILED)
        {
            fprintf(stderr, "[Error] mmap failed: %s\n", strerror(errno));
        }
		else
        {
            //计算控制pin3引脚的寄存器的地址
            bcm2837_gpio_base = bcm2837_peripherals_base + 0x200000 / 4;
			GPFSEL0 = bcm2837_gpio_base + 0x0000 / 4;
			GPFSEL1 = bcm2837_gpio_base + 0x0004 / 4;
            GPFSEL2 = bcm2837_gpio_base + 0x0008 / 4;
			GPFSEL3 = bcm2837_gpio_base + 0x000C / 4;
            GPSET0 = bcm2837_gpio_base + 0x001C / 4;
            GPCLR0 = bcm2837_gpio_base + 0x0028 / 4;
            printf("Virtual address:\n");
            printf("\tPERIPHERALS_BASE -> %X\n", (uint32_t)bcm2837_peripherals_base);
            printf("\tGPIO_BASE -> %X\n", (uint32_t)bcm2837_gpio_base);
            printf("\tGPFSEL0 -> %X\n", (uint32_t)GPFSEL0);
            printf("\tGPSET0 -> %X\n", (uint32_t)GPSET0);
            printf("\tGPCLR0 -> %X\n", (uint32_t)GPCLR0);
        }
        close(memfd);
    }
    else
    {
        fprintf(stderr, "[Error] open /dev/mem failed: %s\n", strerror(errno));
    }
 
    return bcm2837_peripherals_base != MAP_FAILED;
}
 
void pin31_select_output()
{
    uint32_t value = read_addr(GPFSEL3);
    //1111 1111 1111 1111 1111 1111 1100 0111 -> 0xFFFFFFC7
    //0000 0000 0000 0000 0000 0000 0000 1000 -> 0x00000008
    value = (value & 0xFFFFFFC7) | 0x00000008;
    write_addr(GPFSEL3, value);
}
 
void pin3_ctrl(uint8_t level)
{
    volatile uint32_t* reg;
    uint32_t value;
 
    if(level == HIGH)
    {
        reg = GPSET0;
    }
    else if(level == LOW)
    {
        reg = GPCLR0;
    }
 
    value = read_addr(reg);
    //0111 1111 1111 1111 1111 1111 1111 1111 -> 0x7FFFFFFF
    //1000 0000 0000 0000 0000 0000 0000 0000 -> 0x80000000
    value = (value & 0x7FFFFFFF) | 0x80000000;
    write_addr(reg, value);
}
 
void write_addr(volatile uint32_t* addr, uint32_t value)
{
    __sync_synchronize();
    *addr = value;
    __sync_synchronize();
}
 
uint32_t read_addr(volatile uint32_t* addr)
{
    uint32_t value;
 
    __sync_synchronize();
    value = *addr;
    __sync_synchronize();
 
    return value;
}

