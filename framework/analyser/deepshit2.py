
async def analyse_file(ctx,filename=None,formatflag=None,clean_name=None):

    challenge = None
    print(type(ctx))
    if (len(ctx.message.attachments) > 0):filename = ctx.message.attachments[0].url

    # Get Challenge Name
    challenge = ctx.message.channel if hasattr(ctx,'message') else ctx

    # Reload Challenge if no loaded
    if len(challenge_list.keys()) == 0: load(ctx)

    # Cleaned name without 🚩 
    if(clean_name == None): clean_name = challenge.name.split('|')[0].strip().replace("🚩", "")

    # Sanitize Format flag
    if(formatflag == None or formatflag == ''):formatflag = 'flag'
    formatflag = formatflag.replace('{','').replace('}','')
    
    # List all path of file
    all_files = await list_FileQueue(ctx,filename,formatflag,clean_name)

    if(analyse_file == []):
        await ctx.send('**[+] Challenge not found ...**')
    else:

        # Analyses Files
        found = []

        for f in all_files:
            if(os.path.isfile(f)):

                logger('Analysing %s'%f,"info",1,1)
                await ctx.send(f'** [+] Analysing**')
                
                # Call analyse function
                resp,embed_text,flag_found = utils.analyse_file.analysis(f,formatflag)
                
                # Add flag found to the list 
                found += flag_found

                # Embed
                embed = discord.Embed(title="Analysis Result", description="File: "+os.path.basename(f),color=0x00ff00)
                embed.add_field(name="Info : \n", value=embed_text)
                await ctx.send(embed=embed)

                # Send Result
                await send_result(ctx,resp)

                logger('End Analysing',"info",1,0)

                # Send Flag Founded
                if found != []: await ctx.send('**[+] Found: **\n```%s```'%found)

                # End
                await ctx.send('**[+] End Analysing**')

########### OSINT### ########################################################################

@bot.command()
async def mail(ctx,mail=None):
    if(mail == None):await send_result(ctx,['Usage: %semail example@google.com'%PREFIX])
    else:
        logger("Searching mail :  %s ..."%mail,"log",1,0)
        await send_result(ctx,searchemail(mail))

@bot.command()
async def email(ctx,mail=None):
    if(mail == None):
        await send_result(ctx,['Usage: %semail example@google.com'%PREFIX])
    else:
        logger("Searching email :  %s ..."%mail,"log",1,0)
        await send_result(ctx,searchemail(mail))

@bot.command()
async def user(ctx,user=None):
    if(user == None):
        await send_result(ctx,['Usage: %suser Xx_Dark_Killer98_xX'%PREFIX])
    else:
        logger("Searching user :  %s ..."%user,"log",1,0)
        await send_result(ctx,searchuser(user))

@bot.command()
async def phone(ctx,phone=None):
    if(phone == None):
        await send_result(ctx,['Usage: %sphone 0751469XXX'%PREFIX])
    else:
        logger("Searching phone :  %s ..."%phone,"log",1,0)
        await send_result(ctx,searchphone(phone))

@bot.command()
async def image(ctx,image):
    if(image == None):
        await send_result(ctx,['Usage: %simage http://myphotos.com/ABCDEF.png'%PREFIX])
    else:
        logger("Searching image :  %s ..."%image,"log",1,0)
        await send_result(ctx,searchimage(image))

async def send_result(ctx,content):
    for element in content:
        if type(element) == list :
            path_report = element[1]
            if(os.path.isfile(path_report)):                
                # Upload file is Lengt < 8mb
                cnt = element[0]
                try:
                    if sizeok(path_report):
                        await ctx.send(cnt,file=discord.File(path_report))
                        # Remove File
                        os.system('rm %s'%path_report)
                    else:
                        await ctx.send('%s : File is too big %s'%(cnt,path_report))
                except Exception as ex:
                    logger(str(ex),"error",1,1)
                    pass                            
        else:           
            await ctx.send(element)