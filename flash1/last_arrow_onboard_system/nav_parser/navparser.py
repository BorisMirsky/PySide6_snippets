import os
import struct
from pathlib import Path
import pandas as pd
import numpy as np


FORMAT = "="
BUFF_MAX_CHANNEL = 16

def nop(x):
    return x

def convertTo1251(v):
    """
    Перекодируем и убираем хвост из нулей.
    """
    return v.decode("cp1251").split('\x00', 1)[0]
    
class NAV:
    
    @classmethod
    def size(cls):
        return cls.Struct.size
    
    #def __init__(self, struct_bytes):        
    #    parsed = self.__class__.Struct.unpack(struct_bytes)
    #    values = self.__dict__
    #    for i, (fmt, op, name, comment) in enumerate(self.__class__.StructInfo):
    #        values[name] = op(parsed[i])
    
    def __init__(self, struct_bytes):        
        item_start = 0
        values = self.__dict__        
        for (fmt, op, name, comment) in self.__class__.StructInfo:        
            item_end = item_start + struct.calcsize(FORMAT+fmt)            
            parsed = struct.unpack(FORMAT+fmt, struct_bytes[item_start:item_end])
            values[name] = op(parsed) if len(parsed) > 1 else op(parsed[0])        
            item_start = item_end
    
    def __str__(self):
        values = self.__dict__
        return "\n".join( f"{name}:\t\t{values[name]},\t# {comment}" for _, _, name, comment in self.__class__.StructInfo)

class Mash(NAV):
    """
    typedef struct {
        unsigned char  Type,Name[24];
        unsigned int   Number; 		
        unsigned short LR[5],LN[5],T[4],W;
    } tsHMASH;
    """
    
    StructInfo = (
        ("B", nop, "Type", ""), 
        ("24s", convertTo1251, "Name", ""),
        ("I", nop, "Number", ""),
        ("5H", nop, "LR", ""),
        ("5H", nop, "LN", ""),
        ("4H", nop, "T", ""),
        ("H", nop, "W", ""),
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))
            
class InfoCH(NAV):
    """
    typedef struct {
        unsigned char  Val;           
        unsigned char  Type;          
        float          Scale;         
    } tsINFO_CH;
    """
    StructInfo = (
        ("B", nop, "Val", ""), # 
        ("B", nop, "Type", ""),
        ("f", nop, "Scale", ""),
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))
    
class ArrayInfoCH:
    def __init__(self, size: int):
        self.size = size        
    
    def __call__(self, struct_bytes):
        start = 0
        self.items = []
            
        for i in range(self.size):        
            end = start + InfoCH.size()
            ch = InfoCH(struct_bytes[start:end])
            self.items.append(ch)
            start = end
        return self
    
    def __str__(self):        
        return "\n\t".join(f"{i+1}. {ch.__dict__}" for i, ch in enumerate(self.items))

class Picket(NAV):
    """
    typedef struct 
    {
        int            KM;
        short          M, MM; 
    } tsPKT;
    """
    StructInfo = (
        ("i", nop, "KM", ""), 
        ("h", nop, "M", ""),
        ("h", nop, "MM", ""),
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))
    
    @property
    def km_m_mm(self) -> tuple[int,int,int]:
        """
        Если метровая часть пикета > 2000 (а такое бывает), то обнуляем ее.
        """
        return self.KM, 0 if self.M > 2000 else self.M, self.MM
    
    @property
    def km_m_sm(self) -> tuple[int,int,float]:
        """
        Возвращает кортеж из 3-х элементов: (km,m,sm)
        """
        km, m, mm = self.km_m_mm
        return km, m, mm/10

    
class DBN_DOR(NAV):
    """
    typedef struct 
    {
        short		KOD;           // *** Код дороги  
        char 		NAME[30],      // Наименование дороги
                    SNAME[6];      // Краткое наименование
    } tsDBN_DOR;
    """
    StructInfo = (
        ("h", nop, "KOD", ""), 
        ("30s", convertTo1251, "NAME", ""),
        ("6s", convertTo1251, "SNAME", ""),
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))

class DBN_UP(NAV):
    """
    typedef struct 
    {
        int   			ID;            // *** ID участка пути - НАПРАВЛЕНИЕ 
        short 			KOD;           // Код участка
        short 			MAG_KOD;       // Код магистрали
        char  			NAME[50];      // Наименование участка
        int   			STAN1_ID;      // Id раздельного пункта-начало <пусто> !!!!
        int   			STAN2_ID;      // .....................-конец  <пусто> !!!!
    } tsDBN_UP;
    """
    #tsDBN_UP = struct.Struct('ihh50sii')
    StructInfo = (
        ("i", nop, "ID", "ID участка пути - НАПРАВЛЕНИЕ"), 
        ("h", nop, "KOD", "Код участка"),
        ("h", nop, "MAG_KOD", "Код магистрали"),
        ("50s", convertTo1251, "NAME", "Наименование участка"),
        ("i", nop, "STAN1_ID", "Id раздельного пункта-начало <пусто> !!!!"), 
        ("i", nop, "STAN2_ID", ".....................-конец  <пусто> !!!!"), 
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))

class DBN_PUTGL(NAV):
    """
    typedef struct 
    {
        int   			ID;            // *** ID главного пути
        int   			UP_ID;         // ID участка пути - НАПРАВЛЕНИЕ
        char  			NOM[7];        // номер пути
        short 			KOL_SHIR_ID;   // ID ширины пути
        int   			PUTGL_ID_OSN;  // ID осн пути
    } tsDBN_PUTGL;
    """
#    tsDBN_PUTGL = struct.Struct('ii7shi')
    StructInfo = (
        ("i", nop, "ID", "ID главного пути"), 
        ("i", nop, "UP_ID", "ID участка пути - НАПРАВЛЕНИЕ"),
        ("7s", convertTo1251, "NOM", "номер пути"),
        ("h", nop, "KOL_SHIR_ID", "ID ширины пути"),
        ("i", nop, "PUTGL_ID_OSN", "ID осн пути"),         
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))
    
    
class DBN_PEREG_MS(NAV):    
    """
    typedef struct 
    {
        int      		ID;            // ***  МС перегон
        int      		UP_ID;         // ID участка пути
        int      		STAN1_ID;      // Начало
        int      		STAN2_ID;      // Конец
        double   		EXPL;          // Эксплуатационная длина
        char     		NAME[64];
    } tsDBN_PEREG_MS;
    """
#    tsDBN_PEREG_MS = struct.Struct('iiiid64s')
    StructInfo = (
        ("i", nop, "ID", "МС перегон"), 
        ("i", nop, "UP_ID", "ID участка пути"),
        ("i", nop, "STAN1_ID", "Начало"),
        ("i", nop, "STAN2_ID", "Конец"),
        ("d", nop, "EXPL", "Эксплуатационная длина"),
        ("64s", convertTo1251, "NAME", ""),        
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))


class DBN_STAN(NAV):  
    """
    typedef struct 
    {
        int   			ID;				// *** ID раздельного пункта
        int   			KOD;				// Основной код раздельного пункта
        int   			PRED_ID;			// ID отделения 
        int   			OKATO_ID;		// ID ОКАТО
        short 			TIP_ID;			// ID типа разд пункта
        char  			NAME[38];		// Полное  наименование разд пункта
    } tsDBN_STAN;
    """
#    tsDBN_STAN = struct.Struct('iiiih38s')
    StructInfo = (
        ("i", nop, "ID", "ID раздельного пункта"), 
        ("i", nop, "KOD", "Основной код раздельного пункта"),
        ("i", nop, "PRED_ID", "ID отделения"),
        ("i", nop, "OKATO_ID", "ID ОКАТО"),
        ("h", nop, "TIP_ID", "ID типа разд пункта"),
        ("38s", convertTo1251, "NAME", "Полное  наименование разд пункта"),        
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))


class DBN_STANKM(NAV):  
    """
    typedef struct 
    {
        int            PUTGL_ID;   	// *** ID главного пути
        int            STAN_ID;    	// *** ID раздельного пункта
        short          OS_PRIZ_ID; 	// ID признака оси раздел-х пунктов
        int   			KM;         	// Ось, км
        short			M;          	// Ось, м
        int   			KMN;        	// Начало, км
        short 			MN;         	// Начало, м
        int   		KMK;        	// Конец, км
        short 			MK;         	// Конец, м
    } tsDBN_STANKM;
    """
#    tsDBN_STANKM = struct.Struct('iihihihih')
    StructInfo = (
        ("i", nop, "PUTGL_ID", "ID главного пути"), 
        ("i", nop, "STAN_ID", "ID раздельного пункта"),        
        ("h", nop, "OS_PRIZ_ID", "ID признака оси раздел-х пунктов"),
        ("i", nop, "KM", "Ось, км"),
        ("h", nop, "M", "Ось, м"),
        ("i", nop, "KMN", "Начало, км"),
        ("h", nop, "MN", "Начало, м"),
        ("i", nop, "KMK", "Конец, км"),
        ("h", nop, "MK", "Конец, м"),
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))

class Track(NAV):
    """
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
    """
    StructInfo = (
        ("7s", convertTo1251, "NPUT", ""), 
        (f"{Picket.size()}s", Picket, "PKT_BEGIN", ""),
        (f"{Picket.size()}s", Picket, "PKT_END", ""),
        ("h", nop, "ADM_KOD", ""),
        (f"{DBN_DOR.size()}s", DBN_DOR, "DOR", ""),
        (f"{DBN_UP.size()}s", DBN_UP, "UP", ""),
        (f"{DBN_PUTGL.size()}s", DBN_PUTGL, "PUTGL", ""),
        (f"{DBN_PEREG_MS.size()}s", DBN_PEREG_MS, "PEREG_MS", ""),
        (f"{DBN_STAN.size()}s", DBN_STAN, "STAN1", ""),
        (f"{DBN_STANKM.size()}s", DBN_STANKM, "STANKM1", ""),
        (f"{DBN_STAN.size()}s", DBN_STAN, "STAN2", ""),
        (f"{DBN_STANKM.size()}s", DBN_STANKM, "STANKM2", ""),
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))
    
class VPIHeader(NAV):

    def measure_params(v: int) -> dict:
        """
        unsigned short	DirPKT:1,  // Направление съемки: 0-по пикетажу, 1-против пикетажа
                        DirMASH:1, // Направление машины: 0-вперед, 1-назад (вперед - котловая тележка впереди)
                        Press:2,   // Прижим: 0-влево, 1-вправо, 3-по обоим ниткам
                        Horda:1,   
                        IntertrackSpace:2,
                        ReservFlags:9;
        """
        d = dict()
        d['pkt_dir'] = v & 1
        d['machine_dir'] = (v >> 1) & 1
        d['press'] = (v >> 2) & 0b11
        #d['horda'] = (v >> 4) & 1
        return d

    StructInfo = (
        ("6s", nop, "Type", ""),
        ("h", nop, "Version", ""),
        ("I", nop, "Time", ""),
        (f"{Mash.size()}s", Mash, "Mash", ""),
        ("H", measure_params, "Machine", ""),
        ("I", nop, "CntSTEP", ""),
        ("H", nop, "CntMARKER", ""),
        ("H", nop, "CntRFID", ""),
        ("f", nop, "SizeSTEP", ""),
        (f"{InfoCH.size()*BUFF_MAX_CHANNEL}s", ArrayInfoCH(BUFF_MAX_CHANNEL), "InfoCH", ""),
        (f"{Track.size()}s", Track, "Track", ""),
        ("I", nop, "CntFRAG", ""),
        ("I", nop, "CntPOST", ""),
        ("I", nop, "CntSWITCH", ""),
        ("I", nop, "CntBUILD", ""),
        ("I", nop, "CntSPEED", ""),
        ("I", nop, "CntTHREAD", ""),
        ("I", nop, "CntUROV", ""),
        ("I", nop, "CntCURVE", ""),
        ("q", nop, "ID_Trip", ""),
        ("d", nop, "StartCoord", ""),
        (f"{BUFF_MAX_CHANNEL}f", nop, "OffsetCH", ""),
        ("I", nop, "CntDEFECT", ""),
    )    
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))

    @property
    def track(self):
        return self.Track
    @property
    def back_chord_plan(self) -> float:
        return self.Mash.LR[2]/1000
    @property
    def front_chord_plan(self) -> float:
        return self.Mash.LR[1]/1000
    @property
    def back_chord_prof(self):
        return self.Mash.LN[2]/1000
    @property
    def front_chord_prof(self):
        return self.Mash.LN[1]/1000
    @property
    def machine_description(self):
        return f'{self.Mash.Name} №{self.Mash.Number}'
    
class RFID(NAV):
    """
    typedef struct {  
        unsigned int   TS,            // Time stamp (1ms) 
                            STP,      // cчетчик импульсов датчика пути (синхро)
                            ID,       // идентификатор
                            BLOCK[3]; // блоки данных 
        unsigned short State;         // Маска блоков(0..3), кол-во точек(4..14), error(15), 
        double         KRD;           // контрольная длина в м от начала участка по оси пути
    } tsRFID;
    """
    StructInfo = (        
        ("I", nop, "TS", ""), 
        ("I", nop, "STP", ""),
        ("I", hex, "ID", ""),
        ("3I", nop, "BLOCK", ""),
        ("H", nop, "State", ""),
        ("d", nop, "KRD", ""),
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))

class MARKER(NAV):
    """
    typedef struct {
        unsigned char  Type;          // Тип
        double         KRD;           // относит. координата в м (для VPI)
    } tsMARKER_D;
    """
    StructInfo = (        
        ("B", nop, "Type", "Тип"),         
        ("d", nop, "KRD", "относит. координата в м (для VPI)"),
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))
    
    Types = {0: 'ПИКЕТ', 13: 'СТРЕЛКА крестовина', 14: 'СТРЕЛКА остряк'}    
    
    def __init__(self, struct_bytes):
        super().__init__(struct_bytes)
        self.index = int(self.KRD/NAVFile.REC_STEP)
            
    @property
    def type_name(self):
        return self.Types.get(self.Type, 'НЕИЗВЕСТНО')
    
    def __str__(self):
        return f"Type:\t{self.Type} ({self.type_name})\n KRD:\t{self.index} ({self.KRD})"
    
class FRAG(NAV):
    """
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
    """
    StructInfo = (                
        ("d", nop, "KRD", ""),
        ("h", nop, "KMN", ""),
        ("h", nop, "MN", ""),
        ("h", nop, "KMK", ""),
        ("h", nop, "MK", ""),
        ("l", nop, "Kod_napr", ""),
        ("c", ord, "Kod_park", ""),
        ("10s", convertTo1251, "Num_way", ""),
        ("B", nop, "Hod", ""),
        ("51s", convertTo1251, "Name", ""),
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))
    
    def __init__(self, struct_bytes):
        super().__init__(struct_bytes)
        self.index = int(self.KRD/NAVFile.REC_STEP)
    
class DEFECT(NAV):
    """
    typedef struct {                 // Описание НЕИСПРАВНОСТЕЙ
      double          KRD_BEG,       // относит. координата начала, м
                      KRD_END;       // ................... конца, м
      float           Value;         // Отступление (мм)
      unsigned short  Type;          // Тип неисправность (код)
      unsigned short  VPass,         // Ограничение скорости пасс. (км/ч)
                            VGruz,   // .................... груз.
                            VPorog;  // .................... порож.
      unsigned char   Degree;        // Степень отклонения
      unsigned char   Reserv[3];     //
    } tsDEFECT_D;
    """
    StructInfo = (        
        ("d", nop, "KRD_BEG", ""),         
        ("d", nop, "KRD_END", ""),
        ("f", nop, "Value", ""),
        ("H", nop, "Type", ""),
        ("H", nop, "VPass", ""),
        ("H", nop, "VGruz", ""),
        ("H", nop, "VPorog", ""),
        ("H", nop, "Degree", ""),
        ("3H", nop, "Reserv", ""),
    )
    Struct = struct.Struct(FORMAT + "".join(x[0] for x in StructInfo))
    
    def __init__(self, struct_bytes):
        super().__init__(struct_bytes)
        self.index_beg = int(self.KRD_BEG/NAVFile.REC_STEP)
        self.index_end = int(self.KRD_END/NAVFile.REC_STEP)


class NAVFile:
    
    REC_STEP = 0.185
    
    @staticmethod
    def picket_to_metre(km, m, sm) -> float:
        """
        Переводит пикет формата (km, m, sm) в метры.
        """
        result_m = (km * 1000) + m + (sm / 100)
        return result_m

    def __init__(self, filename):
        with open(filename, "rb") as f:
            self.path = filename
            self.header = VPIHeader(f.read(VPIHeader.size()))
            # self.REC_STEP = self.header.CntRFID 
            # collections
            self._data = None
            self._rfids = None
            self._markers = None
            self._frags = None
            self._defects = None
            
    @property
    def name(self):
        return os.path.basename(self.path)
    
    @property
    def rec_count(self):
        return self.header.CntSTEP
    
    @property
    def rec_step(self):
        return self.header.SizeSTEP
           
    @property
    def road_code(self):
        return self.header.track.DOR.KOD
    
    @property
    def road_name(self):
        return self.header.track.DOR.NAME
    
    @property
    def road_sname(self):
        return self.header.track.DOR.SNAME
    
    @property
    def way(self):
        return self.header.track.NPUT

    @property
    def direction(self):
        return self.header.track.UP.KOD
            
    @property
    def pkt_start(self) -> tuple[int,int,int]:
        return self.header.track.PKT_BEGIN.km_m_sm
    
    @property
    def pkt_end(self) -> tuple[int,int,int]:
        return self.header.track.PKT_END.km_m_sm
    
    @property
    def picket_direction(self) -> tuple:
        # 0-по пикетажу, 1-против пикетажа
        d = self.header.Machine['pkt_dir']
        return d, 'по пикетажу' if d == 0 else 'против пикетажа'
    
    @property
    def machine_direction(self) -> tuple:
        # Направление машины: 0-вперед, 1-назад (вперед - котловая тележка впереди)
        d = self.header.Machine['machine_dir']
        return d, 'вперед' if d == 0 else 'назад'
    
    @property
    def machine_press(self) -> tuple:
        # Прижим: 0-влево, 1-вправо, 3-по обоим ниткам
        d = self.header.Machine['press']
        return d, 'влево' if d == 0 else 'вправо'
        
    @property
    def data(self):
        return self._data if self._data is not None else self.read_data()
    
    @property
    def rfid_start(self):
        return self.rec_count*12 + self.header.size() + 65
    
    @property
    def rfid_count(self):
        return self.header.CntRFID 

    @property
    def marker_start(self):
        return self.rfid_start + RFID.size()*self.rfid_count

    @property
    def marker_count(self):
        return self.header.CntMARKER
    
    @property
    def frag_start(self):
        return self.marker_start + MARKER.size()*self.marker_count
    
    @property
    def frag_count(self):
        return self.header.CntFRAG

    @property
    def post_start(self):
        return self.frag_start + FRAG.size()*self.frag_count
    
    @property
    def post_count(self):
        return self.header.CntPOST

    @property
    def switch_start(self):
        return self.post_start + POST.size()*self.post_count
    
    @property
    def switch_count(self):
        return self.header.CntSWITCH
    
    @property
    def build_start(self):
        return self.switch_start + SWITCH.size()*self.switch_count
    
    @property
    def build_count(self):
        return self.header.CntBUILD
    
    @property
    def speed_start(self):
        return self.build_start + BUILD.size()*self.build_count
    
    @property
    def speed_count(self):
        return self.header.CntSPEED

    @property
    def thread_start(self):
        return self.speed_start + SPEED.size()*self.speed_count
    
    @property
    def thread_count(self):
        return self.header.CntTHREAD

    @property
    def urov_start(self):
        return self.thread_start + THREAD.size()*self.thread_count
    
    @property
    def urov_count(self):
        return self.header.CntUROV

    @property
    def curve_start(self):
        return self.urov_start + UROV.size()*self.urov_count
    
    @property
    def curve_count(self):
        return self.header.CntCURVE

    @property
    def defect_start(self):
        return self.curve_start + CURVE.size()*self.curve_count
    
    @property
    def defect_count(self):
        return self.header.CntDEFECT
    
    @property
    def defects(self):
        if self._defects is None:
            self._defects = self.read_defects()
        return self._defects
    
    def read_defects(self):
        defects = []
        if self.defect_count == 0:
            return []
        
        with open(self.path, 'rb') as f:
            s = f.read()            
        
        offset = self.defect_start
        for i in range(self.defect_count):
            d = DEFECT(s[offset:offset+DEFECT.size()])
            offset += DEFECT.size()
            defects.append(d)
        return defects
    
    @property
    def rfids(self):
        if self._rfids is None:
            self._rfids = self.read_rfids()
        return self._rfids
    
    @property
    def rfids_as_dataframe(self):        
        """
        typedef struct {  
            unsigned int   TS,            // Time stamp (1ms) 
                                STP,      // cчетчик импульсов датчика пути (синхро)
                                ID,       // идентификатор
                                BLOCK[3]; // блоки данных 
            unsigned short State;         // Маска блоков(0..3), кол-во точек(4..14), error(15), 
            double         KRD;           // контрольная длина в м от начала участка по оси пути
        } tsRFID;
        """
        df = pd.DataFrame()
        df['Step'] = [rfid.STP for rfid in self.rfids]
        df['ID'] = [rfid.ID for rfid in self.rfids]
        df['KRD'] = [rfid.KRD for rfid in self.rfids]
        df.index += 1
        return df

    
    def read_rfids(self):
        rfids = []
        if self.rfid_count == 0:
            return []
        
        with open(self.path, 'rb') as f:
            s = f.read()
            
        offset = self.rfid_start
        for i in range(self.rfid_count):
            r = RFID(s[offset:offset+RFID.size()])
            offset += RFID.size()
            rfids.append(r)
        return rfids    
        
    @property
    def markers(self):
        if self._markers is None:
            self._markers = self.read_markers()
        return self._markers
    
    def read_markers(self):
        markers = []
        if self.marker_count == 0:
            return []
        
        with open(self.path, 'rb') as f:
            s = f.read()            
        
        offset = self.marker_start        
        for i in range(self.marker_count):
            m = MARKER(s[offset:offset+MARKER.size()])
            offset += MARKER.size()
            markers.append(m)
        return markers
            
    @property
    def frags(self):
        if self._frags is None:
            self._frags = self.read_frags()
        return self._frags
    
    def read_frags(self):
        frags = []
        if self.frag_count == 0:
            return []
        
        with open(self.path, 'rb') as f:
            s = f.read()
        
        offset = self.frag_start        
        for i in range(self.frag_count):
            obj = FRAG(s[offset:offset+FRAG.size()])
            offset += FRAG.size()
            frags.append(obj)
        return frags
            
    def _get_col_array(self, s, start, size, offset=12):        
        col_data = []
        for i in range(size):
            col_data.append(struct.unpack('h', s[start:start+2])[0])
            start += offset
        return np.array(col_data)
        
    def read_data(self) -> pd.DataFrame:
        self._data = pd.DataFrame()
        # read the whole file
        with open(self.path, 'rb') as f:
            s = f.read()        
        
        mes_count = self.header.CntSTEP 
        urov_start, urov_scale = 772, 10
        prof_l_start, prof_r_start, prof_scale = 774, 776, 5
        width_start, width_scale = 778, 10
        plan_start, plan_ctrl_start, plan_scale = 768, 770, 5
        # plan_start, plan_ctrl_start, plan_scale = 1068, 1070, 5
        
        self._data['strelograph_work'] = self._get_col_array(s, plan_start, size=mes_count)/plan_scale
        # Если данные стрел в плане больше 200, то обнуляем.
        # self._data.strelograph_work[self._data.strelograph_work.abs()>200] = 0.0 
        self._data.loc[self._data.strelograph_work.abs()>200, 'strelograph_work'] = 0.0 
        
        self._data['strelograph_control'] = self._get_col_array(s, plan_ctrl_start, size=mes_count)/plan_scale
        # Если данные стрел в плане больше 200, то обнуляем.
        # self._data.strelograph_control[self._data.strelograph_control.abs()>200] = 0.0
        self._data.loc[self._data.strelograph_control.abs()>200, 'strelograph_control'] = 0.0 
        
        self._data['pendulum_work'] = self._get_col_array(s, urov_start, size=mes_count)/urov_scale
        self._data['sagging_left'] = self._get_col_array(s, prof_l_start, size=mes_count)/prof_scale
        self._data['sagging_right'] = self._get_col_array(s, prof_r_start, size=mes_count)/prof_scale
        self._data['width'] = self._get_col_array(s, width_start, size=mes_count)/width_scale

        #self._data.index += 1
        return self._data
    