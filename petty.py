import tweepy
import os
import time
import datetime

auth = tweepy.OAuthHandler("", "")
auth.set_access_token("", "")

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
folder = "C:\\Petty Bot\\"
min_id = int(open(folder + "Files\\min_id.txt").readline())
last_update = time.time()
last_checks = time.time()
time_update = 3600
time_checks = 180


# def limit_handler(cursor):
#    try:
#        while True:
#            yield cursor.next()
#    except tweepy.RateLimitError:
#        time.sleep(300)
def update_list(user):
    with open(folder + user.screen_name + ".txt", "w") as new_file:
        for a in api.followers_ids(user.id):
            new_file.write(str(a) + "\n")
            # print(a)


def check_new_followers():
    for i in tweepy.Cursor(api.followers).items():
        if not os.path.exists(folder + i.screen_name + ".txt"):
            update_list(i)


def unfollows_list(user):
    old_set = set(open(folder + user.screen_name + ".txt").readlines())
    update_list(user)
    new_set = set(open(folder + user.screen_name + ".txt").readlines())
    return old_set - new_set


def send_dm(user_id, new_set):
    new_list = list(new_set)
    mensaje = f"{len(new_list)} accounts are no longer following you since we last checked. They are:\n\n"
    for i in new_list:
        mensaje = mensaje + api.get_user(i).screen_name + "\n"
    api.send_direct_message(user_id, mensaje)


def update_status_id():
    global min_id
    with open(folder + "\\Files\\min_id.txt", "w") as my_file:
        my_file.write(str(min_id))


def check_mentions():
    global min_id
    mentions = api.mentions_timeline(min_id)
    my_followers = api.followers_ids(api.me().id)
    for m in reversed(mentions):
        if m.user.id in my_followers:
            user = m.user
            unfollows = unfollows_list(user)
            send_dm(user.id, unfollows)
            min_id = m.id
    update_status_id()


def update_followers(run_anyways):
    global last_update
    global time_update
    initial_time = time.time()
    elapsed_time = time.time() - last_update
    if elapsed_time >= time_update or run_anyways:
        print("running update")
        for f in api.followers_ids(api.me().id):
            unfollows = unfollows_list(api.get_user(f))
            if len(unfollows) > 0:
                send_dm(f, unfollows)
        last_update = time.time()
        print(f"done running update took {time.time() - initial_time} seconds {datetime.datetime.now()}")
    elif elapsed_time >= time_update - 30:
        print(f"{int(time_update - elapsed_time)} seconds until next update")


def run_checks(run_anyways):
    global last_checks
    global time_checks
    initial_time = time.time()
    elapsed_time = time.time() - last_checks
    if elapsed_time >= time_checks or run_anyways:
        print("running checks")
        check_new_followers()
        check_mentions()
        last_checks = time.time()
        print(f"done running checks, took {time.time() - initial_time} seconds {datetime.datetime.now()}")
    elif elapsed_time >= time_checks - 30:
        print(f"{int(time_checks - elapsed_time)} seconds until next check")


if __name__ == "__main__":
    run_checks(True)
    update_followers(True)
    while True:
        try:
            run_checks(False)
            update_followers(False)
        except tweepy.error:
            pass
        time.sleep(5)
