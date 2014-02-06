#!/bin/sh

celery -A djangotests multi start 4 -l INFO -Q:1 get_testdata_queue -Q:2 exec_function_queue -Q:3 commit_results_queue


