import os # import os
from os.path import exists # checker of file existence
from datetime import datetime, timedelta, date # import datetime and delta time
import miner # import miner class, subclasses, sleep and logging

def get_time_difference(starting_time, hours):
    """
    Counts time difference between current time and given interval in seconds
    :return: float time difference in seconds
    """

    next_cycle = starting_time + timedelta(hours=hours) # get next configurated cycle
    time_difference = next_cycle - datetime.now() # calculate time difference
    if time_difference.total_seconds() <= 0:
        return 0 # start now
    else:  # check if time difference is not smaller than time of execution of miners
        print("Next cycle starts at: " + str(next_cycle))
        return time_difference.total_seconds()

run = True
while run:
    starting_time = datetime.now() # get starting time
    configuration = { # json configuration patern
        "web_service_address": "", # address of web service
        "sleeping_time_hours": 0, # sleeping time between cycles of data mineing
        "request_time_seconds": 5, # sleeping time between requests
        "application_token": 123456789 # application token
    }

    if not os.path.exists("logs"): # check if folder with logs exists or not
        current_directory = os.getcwd() # get current directory
        path = os.path.join(current_directory, "logs") # prepare path of new directory
        os.mkdir(path) # create directory

    new_log_file = 'logs/' + str(date.today()) + '-' + str(datetime.now().hour) + "-" + str(datetime.now().minute) + "-" + str(datetime.now().second) + '.log'
    miner.logging.basicConfig(
        filename=new_log_file,
        filemode='w+',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=miner.logging.INFO,
        datefmt='%d-%m-%y %H:%M:%S'
    )

    miner.logging.info("Starting...")
    configurated = True
    service_access = True
    connection = True
    if exists("configuration.json"): # check if cofiguration file exists
        configuration_data = ""
        with open("configuration.json", "r") as file: # open configuration file
            configuration_data = file.read() # read all text from configuration.json file
            file.close() # close file
        configuration = miner.json.loads(configuration_data) # parse json data from file
        if configuration["web_service_address"] != "": # check if address works
            try:
                req = miner.requests.post(  # send testing request on service
                    url=configuration["web_service_address"],
                    data={
                        "token": configuration["application_token"],
                        "connection_test": True
                    }
                )
                if req.status_code in range(200, 300):  # check server response
                    returned_data = req.json()  # get json data
                    if returned_data["access"]:  # access granted
                        miner.logging.info("Service connected")
                        if configuration["sleeping_time_hours"] is not None and configuration["request_time_seconds"] is not None:  # check if alll needed variables are set
                            miner.logging.info("App configurated succesfully")
                            print("App configurated succesfully")
                        else:
                            miner.logging.error("There are not set all needed configuration variables")
                            print("There are not set all needed configuration variables")
                            configuration = False
                    else:  # service error
                        miner.logging.error(
                            "Service responded with: " +
                            returned_data["error"]["error_code"] +
                            " " +
                            returned_data["error"]["error_message"]
                        )
                        print(
                            "Service responded with: " +
                            returned_data["error"]["error_code"] +
                            " " +
                            returned_data["error"]["error_message"]
                        )
                        configuration = False
                        service_access = False
                elif req.status_code in range(400, 500):  # if web service do not exist
                    miner.logging.error("Web servicer do not exist.")
                    print("Web service do not exist. Check your configuration file.")
                    configuration = False
                    service_access = False
                else:  # negative response from server
                    miner.logging.error("Web service responded with: " + str(req.status_code))
                    print("Web service is currenty unavalible. We will try it again in next iteration")
                    configuration = True
                    service_access = False
            except miner.requests.exceptions.ConnectionError as e: # handle no internet connection
                print("Unable to connect to internet. I will try it again later")
                miner.logging.error("Unable to connect to internet")
                connection = False
            except Exception as e:
                print("Unknown exception: " + str(e))
                miner.logging.error("Unknown exception: " + str(e))
                configuration = False
                connection = False
    else:
        print("Configuration file do not exist")
        miner.logging.error("Configuration file do note exist")
        with open("configuration.json", "w+") as file: # create nonexisting configuration file
            file.write(miner.json.dumps(configuration))
            file.close()

        miner.logging.error("Configuration file created")
        print("Configuration file created")

    if configurated:
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
                        data_miners.append(  # get miner for site
                            getattr(miner, site[3].replace("\n", ""))( # prepare data miner
                                site[2].replace("\n", ""), # miner page
                                site[1], # shop name
                                configuration["application_token"], # token
                                configuration["web_service_address"] # web service address
                            )
                        )
                        miner.logging.info(
                            "Creating new "+ site[0] +" data miner on site: " + site[2].replace("\n", "")
                        )
                    except AttributeError as e: # if miner do not exist
                        print(str(e))
                        miner.logging.error("Unknown data miner: " + str(e))
                    except Exception as e:
                        print(str(e))
                        miner.logging.error("Unknown exception: " + str(e))

                if len(data_miners) > 0:
                    if service_access and connection:
                        miner.logging.info("Starting data miners...")
                        for data_miner in data_miners:  # start all miners
                            miner.logging.info("Starting " + data_miner.shop_name + " " + data_miner.url)
                            data_miner.main_loop(configuration["request_time_seconds"])  # initialize main loop

                        print("Data processed.")
                    else:
                        print("We can not connect to the web service right now. We will try it later again")

                    print("Sleeping...")
                    miner.logging.info("Sleeping...")
                    miner.sleep(get_time_difference(starting_time, configuration["sleeping_time_hours"]))  # repeat
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
    else:
        print("Program was not configurated properly. Please open configuration file and set up app before starting")
        print("Application shut down")
        input("Press ENTER to exit")
        run = False
