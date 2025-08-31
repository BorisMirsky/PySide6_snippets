#define BUFF_MAX_CHANNEL                 	16

typedef struct {
	unsigned int   Year:12, Month:4, Day:5, Hours:5, Minutes:6;
} tsHTIME;

typedef struct {
	unsigned char  Type,Name[24];
	unsigned int   Number; 		
	unsigned short LR[5],LN[5],T[4],W;
} tsHMASH;

typedef struct {
	unsigned char  Val;           
	unsigned char  Type;          
	float          Scale;         
} tsINFO_CH;

typedef struct 
{
	int            KM;
	short          M, MM; 
} tsPKT;
 
typedef struct {
	unsigned int   KM0;        // Начало, км
	unsigned int   M0;         // Начало, м
	unsigned short ID0;        // ID признака границы путей-начало
	unsigned int   KM1;        // Конец, км
	unsigned int   M1;         // Конец, м
	unsigned short ID1;        // ID признака границы путей-конец
} tsGRANPUT;

typedef struct 
{
	short 			KOD;           // *** Код административный  
	short 			STRAN_KOD;     // Код страны  
	char  			NAME[70],      // Наименование 
		 			SNAME_RUS[7],  // Краткое рус. наименование
		 			SNAME_LAT[7];  // Краткое лат. наименование
} tsDBN_ADM;

typedef struct 
{
	short 			KOD;           // *** Код дороги  
	char  			NAME[30],      // Наименование дороги
		 				SNAME[6];      // Краткое наименование
} tsDBN_DOR;

typedef struct 
{
	int   			ID;            // *** ID участка пути - НАПРАВЛЕНИЕ 
	short 			KOD;           // Код участка
	short 			MAG_KOD;       // Код магистрали
	char  			NAME[50];      // Наименование участка
	int   			STAN1_ID;      // Id раздельного пункта-начало <пусто> !!!!
	int   			STAN2_ID;      // .....................-конец  <пусто> !!!!
} tsDBN_UP;

//................... Путь Главный ...................................
typedef struct 
{
	int   			ID;            // *** ID главного пути
	int   			UP_ID;         // ID участка пути - НАПРАВЛЕНИЕ
	char  			NOM[7];        // номер пути
	short 			KOL_SHIR_ID;   // ID ширины пути
	int   			PUTGL_ID_OSN;  // ID осн пути
} tsDBN_PUTGL;

typedef struct 
{
	int				PUTGL_ID;		// *** ID главного пути
	tsGRANPUT 		GRANPUT;   		// Границы участка пути
} tsDBN_PUTGLGRAN;

//................... Станция ...................................
typedef struct 
{
	int   			ID;				// *** ID раздельного пункта
	int   			KOD;				// Основной код раздельного пункта
	int   			PRED_ID;			// ID отделения 
	int   			OKATO_ID;		// ID ОКАТО
	short 			TIP_ID;			// ID типа разд пункта
	char  			NAME[38];		// Полное  наименование разд пункта
} tsDBN_STAN;

typedef struct 
{
	int            PUTGL_ID;   	// *** ID главного пути
	int            STAN_ID;    	// *** ID раздельного пункта
	short          OS_PRIZ_ID; 	// ID признака оси раздел-х пунктов
	int   			KM;         	// Ось, км
	short				M;          	// Ось, м
	int   			KMN;        	// Начало, км
	short 			MN;         	// Начало, м
	int	   		KMK;        	// Конец, км
	short 			MK;         	// Конец, м
} tsDBN_STANKM;

//................... Перегон ...................................
typedef struct 
{
	int      		ID;            // ***  МС перегон
	int      		UP_ID;         // ID участка пути
	int      		STAN1_ID;      // Начало
	int      		STAN2_ID;      // Конец
	double   		EXPL;          // Эксплуатационная длина
	char     		NAME[64];
} tsDBN_PEREG_MS;

typedef struct 
{
	int      		PEREG_MS_ID;   // *** МС перегон
	int      		ID;            // *** МП перегон
	int      		UP_ID;         // ID участка пути
	int      		STAN1_ID;      // Начало
	int      		STAN2_ID;      // Kонец 
	double   		EXDL;          // Эксплуатац длина перегона,м <пусто> !!!
	char     		NAME[80];
} tsDBN_PEREG_MP;

//................... Предприятия ...................................
typedef struct 
{
	int   			ID;				// *** ID предприятия 
	short 			VD_ID;			// ID вида деятельности
	char  			SNAME[40];		// Наименование предприятия краткое
	char  			SNAME2[40];		// Наименование приписки предприятия
	char  			MESTO[40];		// Контора - место
} tsDBN_PRED;

typedef struct 
{
	int   			UP_ID;         // *** ID участка пути - НАПРАВЛЕНИЕ 
	int   			PRED_ID;       // ID предприятия
	short 			UP_KOD;        // Код участка
	short 			MAG_KOD;       // Код магистрали
	char  			NAME[30];      // Наименование участка пути
	tsGRANPUT 		GRANPUT;   		// Границы участка пути
} tsDBN_UCH_PRED;

typedef struct 
{
	int   			PRED_ID;       // *** ID предприятия
	int   			UP_ID;         // *** ID участка пути - НАПРАВЛЕНИЕ 
	int   			PUT_ID;        // *** ID пути предприятия
	int   			PUTGL_ID;      // ID главного пути
	char  			NOM[7];        // номер пути
	short 			KOL_SHIR_ID;   // ID ширины пути
	tsGRANPUT 		GRANPUT;   		// Границы участка пути
} tsDBN_GRANPUT_PRED;


typedef struct {
	char           NPUT[7];      
	tsPKT          PKT_BEGIN;    
	tsPKT          PKT_END;      

	short          ADM_KOD;      
	tsDBN_DOR      DOR;          
	tsDBN_UP       UP;           
	tsDBN_PUTGL    PUTGL;        
	tsDBN_PEREG_MS PEREG_MS;     
	tsDBN_STAN     STAN1;        
	tsDBN_STANKM   STANKM1;      
	tsDBN_STAN     STAN2;         
	tsDBN_STANKM   STANKM2;      
} tsTRACK;

typedef struct {
   __int64     
                  reserv:8,      // пустые - 8 бит (0..7)
                  nProezd:16,    // номер проезда - 16 бит
                  nVagon:10,     // номер вагона - 10 бит
                  Kod_Chechk:4,  // код проверки - 4 бита
                  Mounth:4,      // месяц - 4 бита
                  Year:15,       // год - 15 бит
                  Kod_DOR:7;     // код дороги - 7 бит (57..63)
} tsID_TRIP;

typedef struct
{
	char           Type[6];			
	short          Version;
	tsHTIME        Time;
	tsHMASH        Mash;

	unsigned short	DirPKT:1,      
					DirMASH:1, 
					Press:2,   
					Horda:1,   
					IntertrackSpace:2,
					ReservFlags:9;
					 
	unsigned int	CntSTEP;       
	unsigned short CntMARKER;     	
	unsigned short CntRFID;       	
	float          SizeSTEP;      	

	tsINFO_CH      InfoCH[BUFF_MAX_CHANNEL]; 

	tsTRACK        Track;         

	unsigned int   CntFRAG;       
	unsigned int   CntPOST;       
	unsigned int   CntSWITCH;     
	unsigned int   CntBUILD;      
	unsigned int   CntSPEED;      
	unsigned int   CntTHREAD;    
	unsigned int   CntUROV;      
	unsigned int   CntCURVE;      

	tsID_TRIP      ID_Trip;       
	double         StartCoord;    

	float          OffsetCH[BUFF_MAX_CHANNEL];   
	unsigned int   CntDEFECT;      
	
} tsHEADER_VPI;

typedef struct
{   
	unsigned int   Size;                      // размер Buffer 
	int            iRd, iWr;                  // индексы
	short          *Buff[BUFF_MAX_CHANNEL];   // указатели на данные
	tsINFO_CH      InfoCH[BUFF_MAX_CHANNEL];  // информация о канале
} tsDATA;

typedef struct {  
	unsigned int   TS,            // Time stamp (1ms) 
				  		STP,      // cчетчик импульсов датчика пути (синхро)
				  		ID,       // идентификатор
				  		BLOCK[3]; // блоки данных 
	unsigned short State;         // Маска блоков(0..3), кол-во точек(4..14), error(15), 
	double         KRD;           // контрольная длина в м от начала участка по оси пути
} tsRFID;

typedef struct {
	unsigned char  Type;          // Тип
	double         KRD;           // относит. координата в м (для VPI)
} tsMARKER_D;

typedef struct {                 // описание фрагмента
	double         KRD;           // относит. координата
	short          KMN;           // Начало , км
	short          MN;            // Начало , м
	short          KMK;           // Конец , км
	short          MK;            // Конец, м
	long           Kod_napr;      // код направления/станции Примечание: код станции декорируется битом StanDecor
	char           Kod_park;      // 0 - главные пути и пеpегоны (1-63) станц.пути
	char           Num_way[10];   // индекс пути
	unsigned char  Hod;           // 0-по пикетажу,  1-против пикетажа
	char           Name[51];      // наименование фpагмента
} tsFRAG_D;

typedef struct { 
	double         KRD;           // относит. координата, позиция столба, м
	int            Number;        // номер км
	unsigned char  isPasp;        // 1 - паспортные данные 0 - фактические
} tsPOST_D;

typedef struct {
	double         KRD;           // относит. координата, позиция стрелки, м
	char           Napr;          // напpавление стpелки 0 - неопределенное; 1 - пошерстное; 2 - противошерстное;
	char           Type;          // тип стрелочного перевода
	unsigned short lenR;          // реальная длина стpелки (м.)
	char           Name[5];       // номеp стpелки
	long           stCode;        // код станции(принадлежность) 
								 			// Примечание: код станции декорируется битом StanDecor (const long StanDecor = 1<<30)
	unsigned char  isPasp;       	// 1 - паспортные данные 0 - фактические
} tsSWITCH_D;

typedef struct {                 	// описание мостов, тоннелей
	double         KRD_BEG,       	// относит. координата начала, м
						KRD_END;    // относит. координата конца, м
	short          Type;          	// тип сооружения  0 - неопределен; 1 - безбалластный мост; 2 - балластный мост; 3 - тоннель; 4 - путепровод; 5 - пересечение;
	unsigned char  isPasp;        	// 1 - паспортные данные, 0 - фактические
} tsBUILD_D;

typedef struct {                 	// установленные скорости
	double         KRD_BEG,       	// относит. координата начала, м
						KRD_END;    // относит. координата конца, м
	unsigned short VPass,         	// масксимальная скорость для	пасскажирских
						VGruz,      // ...........................грузовых
						VPorog;     // ...........................порожних
} tsSPEED_D;

typedef struct { 
	double         KRD_BEG,			// относит. координата начала, м
						KRD_END;			// ................... конца, м
} tsTHREAD_D;

typedef struct {                  // возвышение
	double         KRD;           // относит. координата, м
	float          Value;         // значение в точке излома, мм
} tsUROV_D;

typedef struct { // кривые
	double         KRD;           // относит. координата, м
	float          RI,            // радиус кривой, м; 0 - прямая
				   SI,         	  // норма ширины колеи, мм
				   IZ,            // износ, мм
				   DP;            // допуск, мм
} tsCURVE_D;

typedef struct {                 // Описание НЕИСПРАВНОСТЕЙ
  double          KRD_BEG,       // относит. координата начала, м
  						KRD_END; // ................... конца, м
  float           Value;         // Отступление (мм)
  unsigned short  Type;          // Тип неисправность (код)
  unsigned short  VPass,         // Ограничение скорости пасс. (км/ч)
				  		VGruz,   // .................... груз.
				  		VPorog;  // .................... порож.
  unsigned char   Degree;        // Степень отклонения
  unsigned char   Reserv[3];     //
} tsDEFECT_D;

typedef struct   {   
	tsHEADER_VPI	*Header;       
	tsDATA			*Data;         

	tsRFID			*Rfid;          
	tsMARKER_D		*Marker;       

	tsFRAG_D		*Frag;     
	tsPOST_D 		*Post;   
	tsSWITCH_D		*Switch; 
	tsBUILD_D		*Build;  
	tsSPEED_D		*Speed;  
	tsTHREAD_D		*Thread; 
	tsUROV_D		*Urov;     
	tsCURVE_D		*Curve;    
	tsDEFECT_D		*Defect;   
} tsVPI;