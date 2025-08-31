//--------------------------------------------------------------
//--------------------- Define ---------------------------------
//--------------------------------------------------------------

#define DBN_ADM_KOD              20       // Россия 

#define FILE_EXTNAME             ".nav"
#define FILE_TYPE                "WaySRV"                
#define FILE_VERSION             0x0500                  

#define HEADER_SIZE              0x0300                  


//----------------- Машина ---------------------------
#define MASH_TYPE_CORD           0x01      // тросовый                
#define MASH_TYPE_GYROSCOPE      0x02      // гироскоп        
#define MASH_TYPE_OPTIC          0x04      // оптика        

#define MASH_NAME_KVL_P          "КВЛ-П"                
#define MASH_NAME_CNII_4         "ЦНИИ-4"                

//----------------- Каналы ---------------------------
#define MAX_CHANNEL                       16    // Максимальное кол-во каналов

#define CH_VAL_NOT                        0x00     // нет канала
#define CH_VAL_CHAR                       0x01     // 1 байт
#define CH_VAL_UNSIGNED_CHAR              0x02     // 1
#define CH_VAL_SHORT_INTEGER              0x03     // 2
#define CH_VAL_UNSIGNED_SHORT_INTEGER     0x04     // 2
#define CH_VAL_INTEGER                    0x05     // 4
#define CH_VAL_UNSIGNED_INTEGER           0x06     // 4
#define CH_VAL_FLOAT                      0x07     // 4
#define CH_VAL_DOUBLE                     0x08     // 8

#define CH_TYPE_NOT                       0x0     // безразмерная
#define CH_TYPE_mM                        0x1     // МилиМетр
#define CH_TYPE_M                         0x2     // Метр
#define CH_TYPE_DEGREE                    0x3     // Градус
#define CH_TYPE_RADIAN                    0x4     // Радианы
#define CH_TYPE_TSECOND                   0x5     // Время в секудах

//маска каналов
#define CH_MSK_PLANE_LEFT                 0     // План ЛЕВЫЙ      
#define CH_MSK_PLANE_RIGHT                1     // .... ПРАВЫЙ
#define CH_MSK_LEVEL_WORK                 2     // Уровень РАБОЧИЙ
#define CH_MSK_LEVEL_BACK                 3     // ....... ЗАДНИЙ
#define CH_MSK_LEVEL_FRONT                4     // ....... ПЕРЕДНИЙ
#define CH_MSK_PROFILE_LEFT               5     // Профиль ЛЕВЫЙ
#define CH_MSK_PROFILE_RIGHT              6     // ....... ПРАВЫЙ
#define CH_MSK_SHABLON                    7     // Шаблон
#define CH_MSK_COURSE                     8     // Курс (горизонтальный)
#define CH_MSK_GRADIENT                   9     // Уклон (вертикальный)
#define CH_MSK_LATITUDE                   10    // Широта (GPS)
#define CH_MSK_LONGITUDE                  11    // Долгота (GPS)
#define CH_MSK_ALTITUDE                   12    // Высота (GPS)
#define CH_MSK_Reserv_0                   13    // резерв
#define CH_MSK_Reserv_1                   14    // ......
#define CH_MSK_COUNT_IMPULSE              15    // счетчик тиков мерного колеса

//---------------------- RFID ----------------------------
#define RFID_MAX_POINT           0xffff

//---------------------- MARKER ----------------------------
#define MARKER_MAX_POINT         255
#define MARKER_MAX_TYPE          50   // кнопки


//*****************************************************************************
#pragma pack(1)

typedef struct {
   unsigned int   Year:12, Month:4, Day:5, Hours:5, Minutes:6;
} tsHTIME;

typedef struct 
{
   unsigned int   KM;
   unsigned short M, MM; 
} tsPKT;

typedef struct
{
  unsigned char VAL;  // тип данных в канале CH_VAL_XXXX 
  unsigned char TYPE; // тип физических величин СH_TYPE_XXXX
  float SCALE;        // масштаб представления data/SCALE = физические величины

} tsCH_INFO
//-------------------------------------------------------------------------------------
//----------------------------  DB Navigator ------------------------------------------
//-------------------------------------------------------------------------------------
typedef struct 
{
   unsigned short KOD;        // *** Код дороги  
   unsigned char  NAME[30],   // Наименование дороги
                  SNAME[6];   // Краткое наименование
} tsDBN_DOR;

typedef struct 
{
   unsigned int   ID;         // *** ID участка пути
   unsigned short KOD;        // Код участка
   unsigned short MAG_KOD;    // Код магистрали
   unsigned char  NAME[50];   // Наименование участка
   unsigned int   STAN1_ID;   // Id раздельного пункта-начало <пусто> !!!!
   unsigned int   STAN2_ID;   // .....................-конец  <пусто> !!!!
} tsDBN_UP;

//................... Путь Главный ...................................
typedef struct 
{
   unsigned int   ID;            // *** ID главного пути
   unsigned int   UP_ID;         // ID участка пути - НАПРАВЛЕНИЕ
   unsigned char  NOM[7];        // номер пути
   unsigned short KOL_SHIR_ID;   // ID ширины пути
   unsigned int   PUTGL_ID_OSN;  // ID осн пути
} tsDBN_PUTGL;

//................... Станция ...................................
typedef struct 
{
   unsigned int   ID;            // *** ID раздельного пункта
   unsigned int   KOD;           // Основной код раздельного пункта
   unsigned int   PRED_ID;       // ID отделения 
   unsigned int   OKATO_ID;      // ID ОКАТО
   unsigned short TIP_ID;        // ID типа разд пункта
   unsigned char  NAME[38];      // Полное  наименование разд пункта
} tsDBN_STAN;

typedef struct 
{
   unsigned int   PUTGL_ID;      // *** ID главного пути
   unsigned int   STAN_ID;       // *** ID раздельного пункта
   unsigned short OS_PRIZ_ID;    // ID признака оси раздел-х пунктов
   unsigned int   KM;            // Ось, км
   unsigned short M;             // Ось, м
   unsigned int   KMN;           // Начало , км
   unsigned short MN;            // Начало , м
   unsigned int   KMK;           // Конец , км
   unsigned short MK;            // Конец, м
} tsDBN_STANKM;

//................... Перегон ...................................
typedef struct 
{
   unsigned int   ID;            // ***  МС перегон
   unsigned int   UP_ID;         // ID участка пути
   unsigned int   STAN1_ID;      // Начало
   unsigned int   STAN2_ID;      // Конец
   double         EXPL;          // Эксплуатационная длина
   unsigned char  NAME[64];
} tsDBN_PEREG_MS;

typedef struct 
{
   unsigned int   PEREG_MS_ID;   // *** МС перегон
   unsigned int   ID;            // *** МП перегон
   unsigned int   UP_ID;         // ID участка пути
   unsigned int   STAN1_ID;      // Начало
   unsigned int   STAN2_ID;      // Kонец 
   double         EXDL;          // Эксплуатац длина перегона,м <пусто> !!!
   unsigned char  NAME[80];
} tsDBN_PEREG_MP;

//.................. TRACK ..........................
typedef struct {
   unsigned char  NPUT[7];       // номер пути
   tsPKT          PKT_BEGIN;     // начальная позиция 
   tsPKT          PKT_END;       // конечная 

   unsigned short ADM_KOD;       // Административный код гос-ва (DBN_ADM_KOD)
   // обсудить
   tsDBN_DOR      DOR;           // Дорога
   tsDBN_UP       UP;            // Участок пути
   tsDBN_PUTGL    PUTGL;         // Главный путь
   tsDBN_PEREG_MS PEREG_MS;      // Перегон межстанционный
   tsDBN_STAN     STAN1;         // Станция 1
   tsDBN_STANKM   STANKM1;       // Позиция 1
   tsDBN_STAN     STAN2;         // Станция 2
   tsDBN_STANKM   STANKM2;       // Позиция 2

} tsTRACK;

//................. MASH .............................
typedef struct {
   unsigned char  Type, 
                  Name[24]; 
   unsigned int   Number; 
   unsigned short LR[3],      // Плечи Рихтовочной КИС, мм     
                              //  <LR[0] - от передней точки до сканера RFID>
                              //  <LR[1] - от передней до измерительной точки 
                              //  <LR[2] - от измерительной до задней точки 
                  LN[3],      // Плечи Нивелировочной КИС, мм  
                              //  <LN[0] - от передней пиноли до сканера RFID>
                              //  <LN[1] - от передней до измерительной точки 
                              //  <LN[2] - от измерительной до задней точки 
                  W;          // Ширина колеи, мм нормативная
} tsMASH;

//................. HEADER .............................
typedef struct {
   char        Type[6];				// тип дефайном FILE_TYPE
   short       Version;				// FILE_VERSION
   tsHTIME     Time;
   tsMASH      Mash;

   unsigned short    DirPKT:1,      // Направление съемки: 0-по пикетажу, 1-против пикетажа
                     DirMASH:1,     // Направление машины: 0-вперед, 1-назад (вперед - котловая тележка впереди)
                     Press:2;       // Прижим: 0-влево, 1-вправо, 3-по обоим ниткам

   unsigned int      CntSTEP;       // Кол-во шагов (импульсов)
   unsigned short    CntRFID;       // Кол-во меток RFID
   unsigned short    CntMARKER;     // Кол-во маркеров
   float             SizeSTEP;      // Размер шага пути в М (цена импульса)

   tsCH_INFO    ChInfo[MAX_CHANNEL]; // описания каналов
   
   tsTRACK     Track;               // Участок пути

} tsHEADER;


//.................. RFID ..........................
typedef struct {
    unsigned int     TS,             // счетчик тиков (ms)
                     STP,            // счетчик импульсов датчика пути вагона 
                     ID,             // идентификатор
                     Block[3];       // блоки[3...5]
    unsigned short   State;          // маска блоков[0..4], error[15]
   double KRD;		// N*step  
} sRFID;


//.................. MARKER .......................... (кнопки)
typedef struct {  
   unsigned char     Type;           // Тип - расписать 
   unsigned int      STP,            // счетчик импульсов датчика пути вагана
} tsMARKER;

//****************************************************************
//       Структура ФАЙЛА
//****************************************************************

struct _FILE {

   tsHEADER    Header;
   char        HeaderReserv[HEADER_SIZE - sizeof(tsHEADER)];   

// ---------- Массивы данных  -------------------
// размерность и наличие см. Header.TypeValCH[]
for (i=0;i<tsHEADER.CntSTEP;i++)
  {
   short Valid;			// маска валидности даных CH_MSK_*
   for (j=0;j<MAX_CHANNEL;j++)
     {
       if( Header.TypeValCH[j]  & 0x0f )   void  Data_*; 
	 }
  }
// -------------- RFID --------------------------
   if( Header.CntRFID )    tsRFID      Rfid[Header.CntRFID];

// -------------- MARKER ------------------------
   if( Header.CntMARKER )  tsMARKER    Marker[Header.CntMARKER];

}


//------------------------------------------------------------------------
// NN   Канал        Размер (байт)  Тип      Ед.изм     Название
//------------------------------------------------------------------------
// 0  CH_PLANE_Left        4        float    "mМ"     // План ЛЕВЫЙ      
// 1  CH_PLANE_Right       4        float    "mМ"     // .... ПРАВЫЙ
// 2  CH_LEVEL_Work        4        float    "mМ"     // Уровень РАБОЧИЙ
// 3  CH_LEVEL_Back        4        float    "mМ"     // ....... ЗАДНИЙ
// 4  CH_LEVEL_Front       4        float    "mМ"     // ....... ПЕРЕДНИЙ
// 5  CH_PROFILE_Left      4        float    "mМ"     // Профиль ЛЕВЫЙ
// 6  CH_PROFILE_Right     4        float    "mМ"     // ....... ПРАВЫЙ
// 7  CH_SHABLON           4        float    "mМ"     // Шаблон
// 8  CH_COURSE            8        double   "рад"    // Курс (горизонтальный)
// 9  CH_GRADIENT          8        double   "рад"    // Уклон (вертикальный)
// 10 CH_LATITUDE          8        double   "град'   // Широта (GPS)
// 11 CH_LONGITUDE         8        double   "град'   // Долгота (GPS)
// 12 CH_ALTITUDE          4        float    "М'      // Высота (GPS)
// 13 ........             4        .....    "   '    // резерв
// 14 ........             4        .....    "   '    // резерв
// 15 CH_PULSECOUNT        4        int      "имп"    // Счетчик импульсов мерного колеса
//------------------------------------------------------------------------
