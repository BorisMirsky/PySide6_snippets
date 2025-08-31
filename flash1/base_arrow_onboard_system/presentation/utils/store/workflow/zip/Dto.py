# This Python file uses the following encoding: utf-8
from domain.dto.Workflow import MeasuringTripOptionsDto, MeasuringTripResultDto, ProgramTaskCalculationOptionsDto, ProgramTaskCalculationResultDto, LiningTripOptionsDto, LiningTripResultDto, EmergencyExtractionOptionsDto, EmergencyExtractionResultDto
from domain.dto.Travelling import RailPressType, MovingDirection, PicketDirection, LocationVector1D, SteppedData, ProgramTaskBaseData
from domain.dto.Markers import RailwayMarker, RailwayMarkerType, RailwayMarkerLocation
import zipfile
import pandas
import json

#================================================================================
def file_exits(file_path: str, archive: zipfile.ZipFile):
    return True if any([x.endswith(file_path) for x in archive.namelist()]) else False

#================================================================================
# SteppedData
def SteppedData_to_archive(archive: zipfile.ZipFile, path: str, dto: SteppedData) ->None:
    dto.data.to_csv(archive.open(f'{path}/data.csv', 'w'), sep = ';', index = True)
    archive.open(f'{path}/step.txt', 'w').write(str(dto.step.meters).encode('utf-8'))
def SteppedData_from_archive(archive: zipfile.ZipFile, path: str) ->SteppedData:
    return SteppedData(
        data = pandas.read_csv(archive.open(f'{path}/data.csv', 'r'), sep = ';', index_col = 'step'),
        step = LocationVector1D(meters = float(archive.open(f'{path}/step.txt', 'r').readline().decode('utf-8')))
    )
#================================================================================

#================================================================================
# ProgramTaskBaseData
def ProgramTaskBaseData_to_archive(archive: zipfile.ZipFile, path: str, dto: ProgramTaskBaseData) ->None:
    SteppedData_to_archive(archive=archive, path=f'{path}/measurements_processed', dto=dto.measurements_processed)
    pandas.DataFrame(dto.detailed_restrictions).to_csv(archive.open(f'{path}/detailed_restrictions.csv', 'w'), sep = ';', index = True)
    dto.plan.to_csv(archive.open(f'{path}/plan.csv', 'w'), sep = ';', index = True)
    dto.prof.to_csv(archive.open(f'{path}/prof.csv', 'w'), sep = ';', index = True)
    if dto.alc_plan is not None: 
        dto.alc_plan.to_csv(archive.open(f'{path}/alc_plan.csv', 'w'), sep = ';', index = False)
    if dto.alc_level is not None:
        dto.alc_level.to_csv(archive.open(f'{path}/alc_level.csv', 'w'), sep = ';', index = False)
    dto.track_split_plan.to_csv(archive.open(f'{path}/track_split_plan.csv', 'w'), sep = ';', index = False)
    if dto.track_split_prof is not None:
        dto.track_split_prof.to_csv(archive.open(f'{path}/track_split_prof.csv', 'w'), sep = ';', index = False)
    archive.open(f'{path}/step.txt', 'w').write(str(dto.step.meters).encode('utf-8'))
def ProgramTaskBaseData_from_archive(archive: zipfile.ZipFile, path: str) ->ProgramTaskBaseData:
    alc_plan, alc_level = None, None
    track_split_plan, track_split_prof = None, None
    detailed_restrictions = None
    if file_exits(f'{path}/alc_plan.csv', archive):
        alc_plan = pandas.read_csv(archive.open(f'{path}/alc_plan.csv', 'r'), sep = ';')
    if file_exits(f'{path}/alc_level.csv', archive):
        alc_level = pandas.read_csv(archive.open(f'{path}/alc_level.csv', 'r'), sep = ';')
    if file_exits(f'{path}/track_split.csv', archive):
        track_split_plan = pandas.read_csv(archive.open(f'{path}/track_split.csv', 'r'), sep = ';')
    if file_exits(f'{path}/track_split_plan.csv', archive):
        track_split_plan = pandas.read_csv(archive.open(f'{path}/track_split_plan.csv', 'r'), sep = ';')
    if file_exits(f'{path}/track_split_prof.csv', archive):
        track_split_prof = pandas.read_csv(archive.open(f'{path}/track_split_prof.csv', 'r'), sep = ';')
    if file_exits(f'{path}/detailed_restrictions.csv', archive):
        detailed_restrictions = pandas.read_csv(archive.open(f'{path}/detailed_restrictions.csv', 'r'), sep = ';', index_col=0).to_dict('list')

    return ProgramTaskBaseData(
        measurements_processed = SteppedData_from_archive(archive, f'{path}/measurements_processed'),
        detailed_restrictions= detailed_restrictions, 
        plan = pandas.read_csv(archive.open(f'{path}/plan.csv', 'r'), sep = ';', index_col = 'step'),
        prof = pandas.read_csv(archive.open(f'{path}/prof.csv', 'r'), sep = ';', index_col = 'step'),
        alc_plan = alc_plan,
        alc_level = alc_level,
        track_split_plan = track_split_plan,
        track_split_prof = track_split_prof,
        step = LocationVector1D(meters = float(archive.open(f'{path}/step.txt', 'r').readline().decode('utf-8')))
    )
#================================================================================

#================================================================================
# MeasuringTripOptionsDto
def MeasuringTripOptionsDto_to_archive(archive: zipfile.ZipFile, dto: MeasuringTripOptionsDto) ->None:
    archive.open('measuring_trip/options.json', 'w').write(json.dumps({
        'track_title': dto.track_title,
        'start_picket': dto.start_picket.meters,
        'moving_direction': dto.moving_direction.name,
        'picket_direction': dto.picket_direction.name,
        'press_rail': dto.press_rail.name
    }, indent=4, ensure_ascii=False).encode('utf-8'))
def MeasuringTripOptionsDto_from_archive(archive: zipfile.ZipFile) ->MeasuringTripOptionsDto:
    measuring_trip_options_json = json.load(archive.open('measuring_trip/options.json', 'r'))
    return MeasuringTripOptionsDto(
        track_title = measuring_trip_options_json['track_title'],
        press_rail = RailPressType[measuring_trip_options_json.get('press_rail', 'Left')],
        start_picket = LocationVector1D(meters = float(measuring_trip_options_json['start_picket'])),
        picket_direction = PicketDirection[measuring_trip_options_json['picket_direction']],
        moving_direction = MovingDirection[measuring_trip_options_json['moving_direction']])
#================================================================================

#================================================================================
# MeasuringTripResultDto
def MeasuringTripResultDto_to_archive(archive: zipfile.ZipFile, dto: MeasuringTripResultDto) ->None:
    MeasuringTripOptionsDto_to_archive(archive, dto.options)
    SteppedData_to_archive(archive, 'measuring_trip/measurements', dto.measurements)    
    archive.open('measuring_trip/markers.json', 'w').write(json.dumps([{
            'position': position.meters,
            'title': marker.title,
            'type': marker.type.name,
            'location': marker.location.name
        } for marker, position in dto.tags
    ], indent = 4, ensure_ascii = False).encode('utf-8'))
    archive.open('measuring_trip/machine_parameters.json', 'w').write(json.dumps(dto.machine_parameters, indent=4, ensure_ascii=False).encode('utf-8'))
    archive.open('measuring_trip/sensors_mean.json', 'w').write(json.dumps([{
            'strelograph_work': dto.measurements.data.strelograph_work.mean(),
            'sagging_left': dto.measurements.data.sagging_left.mean(),
            'sagging_right': dto.measurements.data.sagging_right.mean(),
            'pendulum_work': dto.measurements.data.pendulum_work.mean(),
            'pendulum_control': dto.measurements.data.pendulum_control.mean(),
            'pendulum_front': dto.measurements.data.pendulum_front.mean()
        }
    ], indent = 4, ensure_ascii = False).encode('utf-8'))
def MeasuringTripResultDto_from_archive(archive: zipfile.ZipFile) ->MeasuringTripResultDto:
    return MeasuringTripResultDto(
        options = MeasuringTripOptionsDto_from_archive(archive), 
        measurements = SteppedData_from_archive(archive, 'measuring_trip/measurements'), 
        tags = [(
            RailwayMarker(title = item['title'], 
                type = RailwayMarkerType[item['type']], 
                location = RailwayMarkerLocation[item['location']]), 
            LocationVector1D(meters = item['position'])
        ) for item in json.load(archive.open('measuring_trip/markers.json', 'r'))],
        machine_parameters = json.load(archive.open('measuring_trip/machine_parameters.json', 'r'))
    )
#================================================================================

#================================================================================
# ProgramTaskCalculationOptionsDto
def ProgramTaskCalculationOptionsDto_to_archive(archive: zipfile.ZipFile, dto: ProgramTaskCalculationOptionsDto) ->None:
    MeasuringTripResultDto_to_archive(archive, dto.measuring_trip)
    # archive.open('program_task/machine_parameters.json', 'w').write(json.dumps(dto.machine_parameters, indent=4, ensure_ascii=False).encode('utf-8'))
    archive.open('program_task/restrictions.json', 'w').write(json.dumps(dto.restrictions, indent=4, ensure_ascii=False).encode('utf-8'))
    archive.open('program_task/options.json', 'w').write(json.dumps({'start_picket': dto.start_picket.meters, 'picket_direction': dto.picket_direction.name}, indent=4, ensure_ascii=False).encode('utf-8'))
def ProgramTaskCalculationOptionsDto_from_archive(archive: zipfile.ZipFile) ->ProgramTaskCalculationOptionsDto:
    program_task_options_json = json.load(archive.open('program_task/options.json', 'r'))
    return ProgramTaskCalculationOptionsDto(measuring_trip = MeasuringTripResultDto_from_archive(archive), 
        # machine_parameters = json.load(archive.open('program_task/machine_parameters.json', 'r')), 
        restrictions = json.load(archive.open('program_task/restrictions.json', 'r')),
        picket_direction = PicketDirection[program_task_options_json['picket_direction']],
        start_picket = LocationVector1D(meters = float(program_task_options_json['start_picket']))
        )
#================================================================================

#================================================================================
# ProgramTaskCalculationResultDto
def ProgramTaskCalculationResultDto_to_archive(archive: zipfile.ZipFile, dto: ProgramTaskCalculationResultDto) ->None:
    ProgramTaskBaseData_to_archive(archive=archive, path='program_task/base', dto=dto.base)
    SteppedData_to_archive(archive=archive, path='program_task/calculated_task', dto=dto.calculated_task)
    ProgramTaskCalculationOptionsDto_to_archive(archive, dto.options)
    if dto.summary is not None:
        dto.summary.to_csv(archive.open('program_task/summary.csv', 'w'), sep = ';', index = False)

def ProgramTaskCalculationResultDto_from_archive(archive: zipfile.ZipFile) ->ProgramTaskCalculationResultDto:
    summary = pandas.read_csv(archive.open('program_task/summary.csv', 'r'), sep = ';') if file_exits('program_task/summary.csv', archive) else None
    return ProgramTaskCalculationResultDto(
                options = ProgramTaskCalculationOptionsDto_from_archive(archive),
                base = ProgramTaskBaseData_from_archive(archive, 'program_task/base'),
                calculated_task = SteppedData_from_archive(archive, 'program_task/calculated_task'),
                summary = summary)
#================================================================================

#================================================================================
# LiningTripOptionsDto
def LiningTripOptionsDto_to_archive(archive: zipfile.ZipFile, dto: LiningTripOptionsDto) ->None:
    ProgramTaskCalculationResultDto_to_archive(archive, dto.program_task)
    if dto.previous_measurements is not None:
        SteppedData_to_archive(archive, 'lining_trip/previous_measurements', dto.previous_measurements)
    
    archive.open('lining_trip/options.json', 'w').write(json.dumps({
        'filename': dto.filename if dto.filename is not None else '',
        'picket_direction': dto.picket_direction.name,
        'current_picket': dto.current_picket.meters,
        'start_picket': dto.start_picket.meters,
        'press_rail': dto.press_rail.name
    }, indent=4, ensure_ascii=False).encode('utf-8'))
def LiningTripOptionsDto_from_archive(archive: zipfile.ZipFile) ->LiningTripOptionsDto:
    lining_trip_options_json = json.load(archive.open('lining_trip/options.json', 'r'))
    return LiningTripOptionsDto(
        filename = lining_trip_options_json.get('filename', ''),
        program_task = ProgramTaskCalculationResultDto_from_archive(archive),
        picket_direction = PicketDirection[lining_trip_options_json['picket_direction']],
        current_picket = LocationVector1D(float(lining_trip_options_json['current_picket'])),
        start_picket = LocationVector1D(float(lining_trip_options_json['start_picket'])),
        press_rail = RailPressType[lining_trip_options_json.get('press_rail', 'Left')],
        # previous_measurements = previous_measurements
        )
#================================================================================

#================================================================================
# LiningTripResultDto
def LiningTripResultDto_to_archive(archive: zipfile.ZipFile, dto: LiningTripResultDto) ->None:
    SteppedData_to_archive(archive, 'lining_trip/measurements', dto.measurements)
    LiningTripOptionsDto_to_archive(archive, dto.options)
def LiningTripResultDto_from_archive(archive: zipfile.ZipFile) ->LiningTripResultDto:
    return LiningTripResultDto(
                options = LiningTripOptionsDto_from_archive(archive),
                measurements = SteppedData_from_archive(archive, 'lining_trip/measurements'))
#================================================================================

#================================================================================
# EmergencyExtractionOptionsDto
def EmergencyExtractionOptionsDto_to_archive(archive: zipfile.ZipFile, dto: EmergencyExtractionOptionsDto) ->None:
    LiningTripResultDto_to_archive(archive, dto.lining_trip)
    SteppedData_to_archive(archive, 'emergency_extraction/extraction_trajectory', dto.extraction_trajectory)
    archive.open('emergency_extraction/parameters.json', 'w').write(json.dumps({
        'start_extraction_picket': dto.start_extraction_picket.meters,
        'slope': dto.slope,
        'velocity': dto.velocity,
        'length': dto.length
    }, indent=4, ensure_ascii=False).encode('utf-8'))
def EmergencyExtractionOptionsDto_from_archive(archive: zipfile.ZipFile) ->EmergencyExtractionOptionsDto:
    parameters = json.load(archive.open('emergency_extraction/parameters.json', 'r'))
    return EmergencyExtractionOptionsDto(
        lining_trip = LiningTripResultDto_from_archive(archive),
        extraction_trajectory = SteppedData_from_archive(archive, 'emergency_extraction/extraction_trajectory'),
        start_extraction_picket = LocationVector1D(meters = float(parameters['start_extraction_picket'])),
        slope = float(parameters['slope']),
        velocity = float(parameters['velocity']),
        length = float(parameters['length'])
    )
#================================================================================

#================================================================================
# EmergencyExtractionResultDto
def EmergencyExtractionResultDto_to_archive(archive: zipfile.ZipFile, dto: EmergencyExtractionResultDto) ->None:
    SteppedData_to_archive(archive, 'emergency_extraction/measurements', dto.measurements)
    EmergencyExtractionOptionsDto_to_archive(archive, dto.options)
def EmergencyExtractionResultDto_from_archive(archive: zipfile.ZipFile) ->EmergencyExtractionResultDto:
    return LiningTripResultDto(options = EmergencyExtractionOptionsDto_from_archive(archive),
        measurements = SteppedData_from_archive(archive, 'emergency_extraction/measurements'))
#================================================================================















