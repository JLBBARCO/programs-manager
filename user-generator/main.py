from lib import log, system, list_programs, json, notifications


operational_system = system.name()
log.info('Start System')
log.info(f'Start Programs Manager User Generator')
log.info(f'Operating System: {operational_system}')


try:
    programs = list_programs.run()
    log.info(f'Number of programs found: {len(programs)}')
    try:
        json.write_json(programs)
        log.info('Programs list saved to JSON file successfully.')
    except Exception as e:
        log.error(f'Error saving JSON file: {e}')
    log.info('Finish Programs Manager User Generator')

except Exception as e:
    log.error(f'Error: {e}')

finally:
    log.info('End System')
    notifications.finalize_notification()

