import time


def activitySerializer(activity):

    encoded = {}
    encoded['id'] = activity.id
    encoded['name'] = activity.name
    encoded['description'] = activity.description
    encoded['startTime'] = activity.start_time.timestamp()
    encoded['endTime'] = activity.end_time.timestamp()
    encoded['place'] = activity.place
    encoded['bookStart'] = activity.book_start.timestamp()
    encoded['bookEnd'] = activity.book_end.timestamp()
    encoded['currentTime'] = time.time()
    encoded['status'] = activity.status
    return encoded