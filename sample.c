
'''
have a firmware which is able to communicate to an app through a function in the code. 
If the data I would like to show does not change, it can display it. 
But if the data I need to show should be changing, it crashes. 
Here is my code. Please note that in order to output data into the app I need to use the tx_cmd_massage, 
and to receive commands from app into the firmware I need this 
if(strncmp((char *)rx_buf, "Start", 3) == 0). Also, 
this firmware is supposed to read the status of the register of a sensor LSM6DSL in real-time:
'''
void user_rxcmd_handle(void * p_context)
{
    uint8_t rx_buf[20];
    uint8_t rx_length=0;
    uint8_t tx_buf[20];

    if(strncmp((char *)rx_buf, "Start", 3) == 0)
    {
        YHdetected = 0;
        YLdetected = 0;
        count = 0;
        while (count < 20)
        {
            uint8_t sdregval;
            LSM6DSL_ACC_GYRO_ReadReg(NULL,LSM6DSL_ACC_GYRO_D6D_SRC,&sdregval,1);
            if(sdregval == LSM6DSL_ACC_GYRO_DSD_YH_DETECTED)
            {
                YHdetected = 1;
                YLdetected = 0;
            }
            else if(sdregval == LSM6DSL_ACC_GYRO_DSD_YL_DETECTED)
            {
                YLdetected = 1;
            }

            if (YHdetected == 1 && YLdetected == 1)
            {
                count = count + 1;
                sprintf((char *)tx_buf, "Count=%d", count);
                tx_cmd_massage(tx_buf,strlen((char *)tx_buf));
                YHdetected = 0;
                YLdetected = 0;
            }
        }
    }
}

//Just for reference, here is the function tx_cmd_massage, please note that I cannot change this since it is necessary to communicate with the App, only the code above:

void tx_cmd_massage(uint8_t *value,uint8_t length)
{
    if (userCmd.tx_cmdList.lock)
        userCmd.tx_cmdList.lock=1;
    if(length<=MAX_AT_CMD_LENGTH)
    {
        buf_get_end(&userCmd.tx_cmdList,value,length);
        tx_timers_start();}
        userCmd.tx_cmdList.lock=0;
    }
}