#!/usr/bin/env python
#import required modules
from datetime import datetime as dt
import sys, random, optparse
try:#python 3
    import urllib.request as req
    from urllib.error import URLError, HTTPError
    three = True
except ImportError:#python 2
    import urllib2 as req
    three = False

#custom header to avoid being blocked by the website
custom_headers = {"User-Agent" : "Mozilla/5.0 (Windows NT {}; rv:{}.0) Gecko/20100101 Firefox/{}.0".format(random.randint(7,11),
                                                                                                           random.randint(40,50),
                                                                                                           random.randint(35,50))}

def adjustDomainName(domain):#correct domain name for urllib
    if domain.startswith("www."):
        domain = domain[4:]
    if not domain.startswith("http"):
        domain = "http://" + domain
    if domain.endswith("/"):
        domain = domain[:-1]
    return domain

def loadWordList(wordlist_file, ext):#load pages to check from dictionary
    try:
        with open(wordlist_file, encoding="utf8") as wlf:
            content = wlf.readlines()
        for i in range(len(content)):
            content[i] = content[i].strip("\n")
        if ext.lower() == "a":
            return content
        else:
            return [element for element in content if element.endswith(ext) or element.endswith("/")]
    except FileNotFoundError:
        sys.exit("WordList dosyası bulunamadı")

def saveResults(file_name, found_pages, progress=0):
    now = dt.now()
    with open("admin_sniffer_results.txt", "a") as f:
        stamp = "%d-%d-%d %d: %d: %d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        print(stamp, file=f)
        for page in found_pages:
            print(page, file=f)
        print("total progress: %d\n______________________________________________" % progress, file=f)

def main(domain, progress=0, ext="a", strict=False, save=True, visible=True, wordlist_file="admin_login.txt"):
    print("Çalışıyor.. durdurmak için ctrl+c basınız.")
    resp_codes = {403 : "request forbidden", 401 : "authentication required"}#HTTP response codes
    found = []#list to hold the results we find
    domain = adjustDomainName(domain)#correct domain name for urllib

    print("wordlist yükleniyor")
    attempts = loadWordList(wordlist_file, ext)
    print("aranıyor...")
    
    for link in attempts[progress:]:#loop over every page in the wordlist file
        try:
            site = domain + "/" + link

            if visible:#show links as they're being tested
                print("deneniyor:", end=" ")

            panel_page = req.Request(site, headers=custom_headers)
            
            try:
                resp = req.urlopen(site)#try visiting the page
                found.append(site)
                print("%s page valid!" % site)

            except HTTPError as e:#investigate the HTTPError we got
                if three:
                    c = e.getcode()
                else:
                    c = e.code()
                    
                if c == 404:
                    if visible:
                        print("%s bulunamadı .." % site)
                else:
                    print("%s Olası Panel.. %s" % (site, resp_codes[c]))
                    if not strict:
                        found.append(site)

            except URLError:
                print("İnternet bağlantısı yok veya geçersiz URL")
                break
            
            except Exception as e2:
                print("hata:{}... {}".format(site, e2))
                continue
            progress += 1
            
        except KeyboardInterrupt:#make sure we don't lose everything should the user get bored
            print()
            break

    if found:
        if save:#save results to a text file
            print("Sonuçlar Kaydediliyor:")
            saveResults("admin_sniffer_results.txt", found)

            print("sonuçlar kaydedildi admin_sniffer_results.txt...")

        print("found the following results: " + "  ".join(found) + " total progress: %s" % progress)

    else:
        print("Herhangi bir Panel bulunamadı\n" \
              + "başka bir wordlist deneyin: %s" % progress)

def getRobotsFile(domain):
    print("Robots.txt Dosyası ekleniyor")
    found = []
    domain = adjustDomainName(domain)#correct domain name for urllib
    
    robots_file = domain + "/robots.txt"
    try:
        data = req.urlopen(robots_file).read().decode("utf-8")
        for element in data.split("\n"):
            if element.startswith("Disallow:"):
                panel_page = domain + element[10:]
                print("Disallow rule found: %s" % (panel_page))
                found.append(panel_page)
        if found:
            print("admin panel bulunamdı sonuç kaydediliyor")
            saveResults("admin_sniffer_results.txt", found, 0)
            print("done...")
        else:
            print("Herhangi bir panel bulunamadı")
    except:
        sys.exit("RoBOTS.TXT bulanamdı")

if __name__ == "__main__":
    print("        +++++++++++++++++++admin_panel_sniffer by MCoury+++++++++++++++++++")
    print("        +                should work with python 2 or 3                   +")
    print("        +           Author not responsible for malicious use!  	+")
    print("        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Türkçeleştiren:Emyounoone\n\n")
    parser = optparse.OptionParser("Usage: python %prog --domain <target domain> " \
                                   + "--progress <index of the page the script reached last run> " \
                                   + "--page_extension <website language> --strict <True or False> " \
                                   + "--save <Save the results to a text file?> " \
                                   + "--verbose <print links as they're tested?> --wordlist <dictionary file to use>" \
                                   + "--robots <if True don't enter anything else except the domain name>")

    domain_help = "hedef domain. örnek: google.com ya da www.example.org"
    progress_help = "(optional) index of the page the script reached last run. The script " \
                    + "displays and saves this value in the results file after every run. "\
                    + "0 starts from the beginning."
    page_extension_help = "(optional) whether the website uses html asp php... default value is 'a' which checks everything"
    strict_mode_help = "(optional, default False) if True, HTTP codes that correspond to forbidden or " \
                       + "authentication required will be ignored."
    save_help = "(optional, default True) if True results will be saved to a txt file."
    verbose_help = "(optional, default True) if True each link will be shown as it's being tested."
    wordlist_help = "(optional, default is the included wordlist) wordlist file to be used."
    robots_help = "(optional, default False) if True the script will try to get the robots.txt " \
                  + "file that usually contains the admin panel. If you set it to True, don't enter" \
                  + "anything else except the target domain."

    parser.add_option("--domain", dest="domain", type="string", help=domain_help)
    parser.add_option("--progress", dest="progress", type="string", help=progress_help)
    parser.add_option("--page_extension", dest="page_ext", type="string", help=page_extension_help)
    parser.add_option("--strict", dest="strict", type="string", help=strict_mode_help)
    parser.add_option("--save", dest="save", type="string", help=save_help)
    parser.add_option("--verbose", dest="verbose", type="string", help=verbose_help)
    parser.add_option("--wordlist", dest="wordlist", type="string", help=wordlist_help)
    parser.add_option("--robots", dest="robots", type="string", help=robots_help)

    (options, args) = parser.parse_args()

    if not options.domain:
        sys.exit("Hedef Domaini giriniz:\n\n%s" % parser.usage)

    try:
        strict_mode = eval(options.strict.title())
    except:
        strict_mode = False

    try:
        save = eval(options.save.title())
    except:
        save = True

    try:
        verbose = eval(options.verbose.title())
    except:
        verbose = True

    if not options.page_ext:
        page_ext = 'a'
    else:
        page_ext = options.page_ext

    if not options.progress:
        progress = 0
    else:
        progress = int(options.progress)

    if not options.wordlist:
        wordlist = "admin_login.txt"
    else:
        wordlist = options.wordlist

    try:
        robots = eval(options.robots.title())
    except:
        robots = False

    if robots:
        getRobotsFile(options.domain)
    else:
        main(options.domain, progress, page_ext, strict_mode, save, verbose, wordlist)
