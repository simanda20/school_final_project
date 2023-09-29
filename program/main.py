import os # import os
from os.path import exists # checker of file existence
from datetime import datetime, timedelta, date # import datetime and delta time
import miner # import miner class, subclasses, sleep and logging

def get_time_difference():
    """
    Counts time difference between 1 AM and current time in seconds
    :return: float time difference in seconds
    """
    current_time = datetime.now() # get current time
    next_cycle = current_time + timedelta(hours=3) # get next 3 hours
    time_difference = next_cycle - current_time # calculate time difference
    return time_difference.total_seconds() # convert time difference to seconds and return

run = True
while run:
    if not os.path.exists("logs"): # check if folder with logs exists or not
        current_directory = os.getcwd() # get current directory
        path = os.path.join(current_directory, "logs") # prepare path of new directory
        os.mkdir(path) # create directory

    miner.logging.basicConfig(
        filename='logs/' + str(date.today()) + '.log',
        filemode='w+',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=miner.logging.INFO,
        datefmt='%d-%m-%y %H:%M:%S'
    )
    miner.logging.info("Starting...")
    if exists("pages.csv"):  # check existention of shop configuration file
        sites = []
        data_miners = []
        miner.logging.info("Reading file with pages...")
        with open("pages.csv", "r") as file:  # open file and read data
            sites = file.readlines()
            file.close()

        miner.logging.info("Processing data...")
        if len(sites) > 0:  # if are there any data
            for site in sites:
                site = site.split(";")  # initialize data miners
                try: # set miners
                    data_miners.append(getattr(miner, site[3].replace("\n", ""))(site[2].replace("\n", ""), site[1]))  # get miner for site
                    miner.logging.info("Creating new "+ site[0] +" data miner on site: " + site[2].replace("\n", ""))
                except AttributeError as e: # if miner do not exist
                    print(str(e))
                    miner.logging.error("Unknown data miner: " + str(e))
                except Exception as e:
                    print(str(e))
                    miner.logging.error("Unknown exception: " + str(e))

            if len(data_miners) > 0:
                miner.logging.info("Starting data miners...")
                for data_miner in data_miners:  # start all miners
                    miner.logging.info("Starting " + data_miner.shop_name + " " + data_miner.url)
                    data_miner.main_loop()

                miner.logging.info("Sleeping...")
                miner.sleep(get_time_difference())  # repeat
            else:
                miner.logging.error("File has not any valid data miners")
                print("File has not any valid data miners.")
                print("Please add your shops in csv format and start app again.")
                print("ShopName;ProductType;SearchedLink with $page pointer;name of dataminer")
                run = False
                miner.logging.info("Application shutdown")
                input("Press ENTER to exit")
        else:
            miner.logging.error("File is empty")
            print("File has not data inside.")
            print("Please add your shops in csv format and start app again.")
            print("ShopName;ProductType;SearchedLink with $page pointer;name of dataminer")
            run = False
            miner.logging.info("Application shutdown")
            input("Press ENTER to exit")
    else:
        miner.logging.error("File does not exist")
        with open("pages.csv", "x") as file:  # create file if not exist
            file.write("")
            miner.logging.info("Creating file...")
            print("File 'pages.csv' had been created.")
            print("Please add your shops in csv format and start app again.")
            print("ShopName;ProductType;SearchedLink with $page pointer;name of dataminer")
            file.close()
        run = False
        miner.logging.info("Application shutdown")
        input("Press ENTER to exit")
