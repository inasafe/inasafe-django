# coding=utf-8
import logging

from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from realtime.app_settings import LOGGER_NAME
from realtime.models.ash import Ash
from realtime.tasks.ash import (
    generate_event_report, run_ash_analysis, generate_ash_report)

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/18/16'


LOGGER = logging.getLogger(LOGGER_NAME)


LOGGER.info('Ash Signals registered')


# TODO: These ifs are ugly, need to refactor it.
@receiver(post_save, sender=Ash)
def ash_post_save(sender, **kwargs):
    """Extract impact layer of the flood"""
    try:
        instance = kwargs.get('instance')
        if isinstance(instance, Ash):
            # Only do processing when it is a new ash
            if instance.task_status and not instance.task_status == 'None':
                # If success, check if the analysis is running or not
                if instance.task_status == 'SUCCESS':
                    # It's either pending or success, do nothing
                    if (instance.analysis_task_status and not
                            instance.analysis_task_status == 'None'):
                        # If the analysis is success
                        if instance.analysis_task_status == 'SUCCESS':
                            # If the report task is not None
                            if (instance.report_task_status and not
                                    instance.report_task_status == 'None'):
                                return
                            # If the report task is None, need to generate
                            else:
                                LOGGER.info('Sending task generate report.')
                                result = generate_ash_report.delay(instance)
                                instance.report_task_id = result.id
                                instance.report_task_status = 'PENDING'
                                instance.save()
                        else:
                            return
                    # No task status, or status == None, need to run the task.
                    else:
                        LOGGER.info('Sending task run analysis.')
                        result = run_ash_analysis.delay(instance)
                        instance.analysis_task_id = result.id
                        instance.analysis_task_status = 'PENDING'
                        instance.save()
                else:
                    return
            else:
                LOGGER.info('Sending task ash processing.')
                result = generate_event_report.delay(instance)
                instance.task_id = result.id
                instance.task_status = 'PENDING'
                instance.save()
    except BaseException as e:
        LOGGER.exception(e)
