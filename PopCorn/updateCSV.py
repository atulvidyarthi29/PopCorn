import csv


def calculate_earning(earn):
        li = []
        new_li = []
        li = earn.split('\n')
        li.pop()
        if(len(li) > 1):
            del li[1:]
        if(li):
            new_li = li[0].split(' ')
        
        if(len(new_li)>2):
            del new_li[2:]
        
        if(len(new_li)>1):
            del new_li[0]
        
        if (not new_li or not ('$' in new_li[0] or 'INR' in new_li[0])):
            new_li = None
        elif new_li:
            new_li = new_li[0].strip('\n').strip(' ').strip(',')
        
        return new_li

def runtime(runtimeIter):

    final_l = runtimeIter.split('\n')
    final_l.pop()
    if(len(final_l)>2):
        final_l.pop()
    del final_l[0]
    if(len(final_l) > 1):
        del final_l[1:]
    temp = final_l[0].split(' ')
    list_a = list(temp[0])
    if(len(list_a) > 0 and (ord(list_a[0]) >= 48 and ord(list_a[0]) <= 57)):
        pass
    else:
        temp[0] = None
    
    return temp[0]

with open('combined_csv1.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)

    with open('data.csv', 'w') as new_file:
        fieldnames = ['\ufefftitle1', 'release_date', 'country', 'poster', 'link_trailer', 'story', 'final_genres', 'taglines', 'runtime_final', 'earning', 'final_budget', 'language', 'final_writers', 'director', 'final_actors', 'imdb'] 
    
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)

        csv_writer.writeheader()
        final_l = []

        for line in csv_reader:
            update = line['country'].split(' ')
            line['country'] = update[len(update) - 1]

            tag = line['taglines']
            if(tag):
                tag = tag.split('\n')
            else:
                new_tag = line['\ufefftitle1']
                tag = ['', new_tag]

            line['runtime_final'] = runtime(line['runtime_final'])
            line['earning'] = calculate_earning(line['earning'])
            line['final_budget'] = calculate_earning(line['final_budget'])

            if(line['final_budget'] == None and line['earning'] == None):
                pass
            
            if(line['final_budget'] == None and line['earning']):
                try:
                    value = line['earning'].split('$')[1].split(",")
                    k = ''
                    for i in value:
                        k+=str(i)

                    line['earning']=int(k.strip())    
                    line['final_budget'] = '$'+ str(2*line['earning'])

                except:
                    pass
            
            if(line['final_budget'] and line['earning'] == None):
                try:
                    value = line['final_budget'].split('$')[1].split(",")
                    k = ''
                    for i in value:
                        k+=str(i)

                    line['final_budget']=int(k.strip())    
                    line['earning'] = '$'+ str(2*line['final_budget'])

                except:
                    pass
            if(line['final_budget'] and line['earning'] == None):
                try:
                    value = line['final_budget'].split('$')[1].split(",")
                    k = ''
                    for i in value:
                        k+=str(i)

                    line['final_budget']=int(k.strip())    
                    line['earning'] = 'INR'+ str(2*line['final_budget'])

                except:
                    pass
            if(line['final_budget'] == None and line['earning']):
                try:
                    value = line['earning'].split('INR')[1].split(",")
                    k = ''
                    for i in value:
                        k+=str(i)

                    line['earning']=int(k.strip())    
                    line['final_budget'] = 'INR'+ str(2*line['earning'])
                except:
                    pass

            lang = line['language']
            new_lang = lang.split('[')
            del new_lang[0]
            new_lang = new_lang[0].split(']')
            new_lang.pop()
            final_len = []
            if(new_lang):
                final_len = new_lang[0].split(',')
            fl = []
            for i in final_len:
                fl.append(''.join(iii for iii in i if iii.isalnum() and iii!=' ').strip('n'))
            
            if(len(fl) == 0):
                fl.append('English')

            if(fl[0] == ''):
                fl[0] = 'English'

            if(fl[0][0].isdigit()):
                fl[0] = 'English'
            
            if(fl[0] in [ 'OfficialSite', 'OfficialFacebook']):
                fl[0] = 'English'
            line['language'] = fl
            csv_writer.writerow(line)