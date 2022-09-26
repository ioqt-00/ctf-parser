    # If not challenge Loaded > Load saved from files
    if(len(challenge_list.keys()) == 0):
        load(None,True)

   # If author as permissions
    if ctx.author.guild_permissions.manage_channels:

        # Start Create CTFD
        logger("Creating CTFD channel","info",1,0)
        

 # If login Succeed
        if islogged != False:

            # Create Channel
            await createchannel(ctx, channel_name)

            # Get Channel Object
            logger("Logged in with user: %s"%CONFIG['u'],"log",0,1)
            await ctx.send("**[+] Logged in with user: %s**"%CONFIG['u'])
            channels = bot.get_all_channels()
            channel = discord.utils.get(channels, name=channel_name)    # Success
            
            # Start Parsing
            await start(ctx, channel)  # Start

            # Save in config.json
            saveconfig(channel_name)
        else:
            # Invalid Creds
            await ctx.reply("**Invalid Credentials or url**")  
        
        logger("Thread Creation END","info",0,1)
    else:
        logger(' [*] {0.author} not allowed.'.format(ctx),"error",1,0)
        await ctx.send("**[*] You are not allowed to run this command!**")  # Action Not Permitted
