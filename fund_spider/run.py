import scrapy.cmdline

#Your Spider Class...

def main():
    #scrapy.cmdline.execute(['scrapy', 'crawl', 'company'])
    scrapy.cmdline.execute(['scrapy', 'crawl', 'Manager'])

if __name__ == '__main__':
    main()
