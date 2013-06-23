#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of frestq.
# Copyright (C) 2013  Eduardo Robles Elvira <edulix AT wadobo DOT com>

# frestq is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# frestq  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with frestq.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from apscheduler.scheduler import Scheduler
from apscheduler.threadpool import ThreadPool
from apscheduler.util import convert_to_datetime

INTERNAL_SCHEDULER_NAME = "internal.frestq"

class NowTrigger(object):
    def __init__(self):
        pass

    def get_next_fire_time(self, start_date):
        return start_date

    def __str__(self):
        return 'now'

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__)


class FThreadPool(ThreadPool):
    def submit(self, func, *args, **kwargs):
        return super(FThreadPool, self).submit(func, *args, **kwargs)


class FScheduler(Scheduler):
    _schedulers = dict()

    def __init__(self, **options):
        gconfig = {
            'apscheduler.threadpool': FThreadPool()
        }
        super(FScheduler, self).__init__(gconfig, **options)

    @staticmethod
    def get_scheduler(queue_name):
        '''
        returns a scheduler for a spefic queue name
        '''
        if queue_name in FScheduler._schedulers:
            return FScheduler._schedulers[queue_name]

        FScheduler._schedulers[queue_name] = sched = FScheduler()
        sched.queue_name = queue_name
        return sched

    @staticmethod
    def reserve_scheduler(queue_name):
        return FScheduler.get_scheduler(queue_name)

    @staticmethod
    def start_all_schedulers():
        '''
        Starts all the statically registered schedulers. It will also adjust
        the maximum number of threads now. This is not done in a previous stage
        because in frestq the app config is not guaranteed to be completely
        setup until this moment.
        '''
        from .app import app

        FScheduler.reserve_scheduler(INTERNAL_SCHEDULER_NAME)
        queues_opts = app.config.get('QUEUES_OPTIONS', dict())

        for queue_name, sched in FScheduler._schedulers.iteritems():
            print "starting %s scheduler" % queue_name

            opts = queues_opts.get(queue_name, dict())
            if 'max_threads' in opts:
                print "setting scheduler for queue %s with "\
                    "max_threads = %d " %(queue_name, opts['max_threads'])
                sched._threadpool.max_threads = opts['max_threads']

            sched.start()

    def add_now_job(self, func, args=None, kwargs=None, **options):
        """
        Schedules a job to be completed as soon as possible.
        Any extra keyword arguments are passed along to the constructor of the
        :class:`~apscheduler.job.Job` class (see :ref:`job_options`).

        :param func: callable to run at the given time
        :param name: name of the job
        :param jobstore: stored the job in the named (or given) job store
        :param misfire_grace_time: seconds after the designated run time that
            the job is still allowed to be run
        :type date: :class:`datetime.date`
        :rtype: :class:`~apscheduler.job.Job`
        """

        print "adding job in sched for queue %s" % self.queue_name
        trigger = NowTrigger()
        options['max_runs'] = 1
        return self.add_job(trigger, func, args, kwargs, **options)
