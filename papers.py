import os
import time
import fitz
import json
import pyDes
import base64
import PyPDF2
import hashlib
import pikepdf
import binascii
import requests
import urllib.parse
from pyDes import *

class RMRB:

    def getYMD(self):
        return time.strftime("%Y-%m/%d", time.localtime())

    def getLen(self):
        u = "http://paper.people.com.cn/rmrb/html/{}/nbs.D110000renmrb_01.htm".format(self.getYMD())
        req = requests.get(u)
        req_str = str(req.content.decode('utf-8'))
        return req_str.count('版：')

    def rmrb(self, path, mode):
        if int(mode) == 0:
            date = getDate()
            YMD = self.getYMD()
        else:
            date = str(mode)
            YMD = time.strftime("%Y-%m/%d", time.strptime(date, "%Y%m%d"))

        print("Input Params: Path={path}, Date={date}".format(path=path, date=date))
        length = self.getLen()
        for index in range(length):
            if int(date) <= 20200630:
                u = "http://paper.people.com.cn/rmrb/page/{YMD}/{index:0>2d}/rmrb{date}{index:0>2d}.pdf".format(YMD=YMD, date=date, index=index+1)
            else:
                u = "http://paper.people.com.cn/rmrb/images/{YMD}/{index:0>2d}/rmrb{date}{index:0>2d}.pdf".format(YMD=YMD, date=date, index=index+1)
            downFile(u, path+"rmrb_"+str(date)+"_"+str(index+1)+".pdf")
        print("RMRB Down Complete!")
        if mergePDF(length, "rmrb_", path, date):
            print("RMRB Merge Complete!")
            for index in range(length):
                os.remove(path+"rmrb_"+str(date)+"_"+str(index+1)+".pdf")
            print("RMRB Delete Complete!")

class BJYB:

    def getYMD(self):
        return time.strftime("%Y-%m/%d", time.localtime())

    def getHtml(self):
        u = "http://epaper.ynet.com/html/{}/node_1331.htm".format(self.getYMD())
        req = requests.get(u)
        return str(req.content.decode('utf-8'))

    def bjyb(self, path, mode):
        if int(mode) == 0:
            date = getDate()
            YMD = self.getYMD()
        else:
            date = str(mode)
            YMD = time.strftime("%Y-%m/%d", time.strptime(date, "%Y%m%d"))

        print("Input Params: Path={path}, Date={date}".format(path=path, date=date))
        URL_LEN = 39
        req_str = self.getHtml()
        pdfnum = req_str.count('.pdf')
        start = 0
        for index in range(pdfnum):
            end = req_str.find('.pdf', start)
            baseurl = req_str[end-URL_LEN:end]
            start = end+4
            url = "http://epaper.ynet.com" + baseurl + ".pdf"
            downFile(url, path+"bjyb_"+str(date)+"_"+str(index+1)+".pdf")
        print("BJYB Down Complete!")
        if mergePDF(pdfnum, "bjyb_", path, date):
            print("BJYB Merge Complete!")
            for index in range(pdfnum):
                os.remove(path+"bjyb_"+str(date)+"_"+str(index+1)+".pdf")
            print("BJYB Delete Complete!")

    #北青报官网偶发缺失某版的情况，原算法暂时废弃
    '''
    def bjyb(self):
        SEQ_ARR = ['A', 'B', 'C', 'D']
        seq = 0
        num = 0
        flag = 0
        namenum = 1
        paper = ["bjqnb", "bjbqb"]
        reqstr = self.getHtml()
        #print(reqstr)
        lenSum = reqstr.count('版：')-2
        length = lenSum
        for index in range(lenSum+1):
            print("index="+str(index))
            flag = 0
            for p in range(2):
                print("p="+str(p))
                print("seq="+str(seq))
                #print(("{paper}{date}{SEQ}{i:0>2d}.pdf").format(SEQ=SEQ_ARR[seq], i=num+1, date=getDate(), paper=paper[p]))
                if reqstr.find(("{paper}{date}{SEQ}{i:0>2d}.pdf").format(SEQ=SEQ_ARR[seq], i=num+1, date=getDate(), paper=paper[p])) != -1:
                    u = "http://epaper.ynet.com/images/{YMD}/{SEQ}{index:0>2d}/{paper}{date}{SEQ}{index:0>2d}.pdf".format(YMD=self.getYMD(), SEQ=SEQ_ARR[seq], date=getDate(), index=num + 1, paper=paper[p])
                    print(u)
                    #downFile(u, "bjyb" + str(namenum) + ".pdf")
                    namenum+=1
                    flag = 1
                    break
            if flag == 0:
                seq += 1
                lenSum -= num
                num = -1
            num += 1

        if mergePDF(length, "bjyb"):
            for index in range(lenSum):
                os.remove("bjyb"+str(index+1)+".pdf")
    '''

class TTZB:

    def init2cipher(self, text):
        out_str = base64.b64decode(text)
        return str(out_str.hex())

    def unCompileCode(self, code):
        c = ""
        for index in range(len(code)):
            c += chr(ord(code[index]) - 1 ^ index)
        return c

    def DesECB(self, cipher, key):
        iv = ""
        k = des(key[0:8], ECB, iv, pad=None, padmode=PAD_PKCS5)
        de = k.decrypt(binascii.a2b_hex(cipher), padmode=PAD_PKCS5)
        return str(de)

    def getText(self, pdfID):
        u = "http://www.ttplus.cn/reader.html?pdfId=" + str(pdfID)
        c = {"SESSION": TTZB_COOKIE}
        r = requests.get(url=u, cookies=c)
        req = r.content.decode("utf-8")
        s = req.find("webViewerLoad")
        rearr = []
        e = req.find(";", s)
        st = req[s + 15:e - 2]
        starr = st.split(",")
        # print(starr[0][2:])
        rearr.append(starr[0][:-1])
        rearr.append(starr[1][2:])
        return rearr
        # return starr[1][2:]

    def getPDF(self, path, url, name):
        req = requests.get(url)
        # print(req.content)
        with open(path + name, "wb") as f:
            f.write(req.content)
        f.close()
        return True

    def dePDF(self, path, srcname, pwd):
        pdf = pikepdf.open(path + srcname, password=pwd[2:-1])
        pdf.save(path + "已解密 " + srcname)

    def getSign(self, kvs):
        VER = "_VER"
        VER_CURRENT_VAL = "1.0"
        SIGN_CURRENT_SECRET = "a7ff2586301b42eea962e9b9c8709689"
        nkvs = ""
        l = []
        kvs[VER] = VER_CURRENT_VAL
        for k in kvs:
            v = kvs[k]
            l.append(k + "=" + v + "&")
        l.sort(key=str.lower)
        nkvs += ''.join(l) + "key=" + SIGN_CURRENT_SECRET
        result = hashlib.md5(nkvs.encode('utf-8'))
        sign = str(result.hexdigest().upper())
        return sign

    def getParam(self, year, sign):
        # ttzb type=11
        # kvs = {"typeId": 11 ,"year": year, "pageSize": 30, "pagenum": 0, "_VER":1.0, "_SIGN":sign}
        st = "typeId=11&year=" + str(year) + "&pageSize=130&pagenum=0&_VER=1.0&_SIGN=" + sign
        return st

    def getAPI(self, param):
        # print(param)
        name = {}
        u = "https://api.ttplus.cn/h5/pdf/all"
        h = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
        r = requests.post(url=u, data=param, headers=h)
        # req = r.content.decode('utf-8')
        rj = r.json()
        for index in range(len(rj["content"]["newsdatas"])):
            id = rj["content"]["newsdatas"][index]["id"]
            title = rj["content"]["newsdatas"][index]["title"] + ".pdf"
            name[id] = title
        # print(rj["content"]["newsdatas"][0])
        return name

    def getOne(self, id):
        kvs = {"newspaperId": str(id), "userId": TTZB_USERID}
        sign = self.getSign(kvs)
        st = "newspaperId=" + str(id) + "&userId=" + str(TTZB_USERID) + "&_VER=1.0&_SIGN=" + sign
        u = "https://api.ttplus.cn/h5/pdf/one"
        h = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
        r = requests.post(url=u, data=st, headers=h)
        rj = r.json()
        name = rj["content"]["newspapertype"] + " " + rj["content"]["updatetime"] + ".pdf"
        # print(name)
        return name

    def ttzb(self, path, TTZB_PARAM):
        pdfID = TTZB_PARAM
        name = self.getOne(pdfID)
        rearr = self.getText(pdfID)
        text = rearr[1]
        cipher = self.init2cipher(text)
        key = self.unCompileCode(TTZB_CODE)
        pdfkey = self.DesECB(cipher, key)
        print("key:" + pdfkey)
        url = rearr[0]
        print("url:" + url)
        self.getPDF(path, url, name)
        print("TTZB Down Complete!")
        self.dePDF(path, name, pdfkey)
        os.remove(path + name)
        os.rename(path + "已解密 " + name, path + name)
        print("TTZB Decrypt Complete!")

class ZQB:

    def getInkey(self, pid):
        u = "http://www.dooland.com/magazine/online_htm5.php?pid=" + str(pid)
        r = requests.get(url=u)
        res = r.content.decode("utf-8")
        s = res.find("data-inkey=")
        return res[s + 12:s + 44]

    def getDest(self, pid, inkey):
        u = "http://www.dooland.com/magazine/InterFace/s_EchoXml_Streamv2_htm5.php?pid=" + str(pid) + "&inkey=" + str(inkey) + "&uid=" + ZQB_UID
        h = {"cookies": ZQB_COOKIE}
        r = requests.get(url=u, headers=h)
        res = r.content.decode("utf-8")
        return str(res)

    def bingo_decode(self, dest, key):
        keyLength = len(key)
        keyArray = []
        for index in range(keyLength):
            keyArray.append((ord(key[index]) % 6))

        destTemp = "";
        for index in range(len(dest)):
            destTemp += (chr(ord(dest[index]) - keyArray[index % keyLength]))
        source = urllib.parse.unquote(destTemp)
        return source

    def src2url(self, source):
        urlArr = []
        start = 0
        num = int(int(source.count(".jpg")) / 2)
        for index in range(num):
            a = source.find('+src=', start)
            b = source.find('+ssrc=', start)
            start = b + 1
            # print(source[a+6: b-1])
            urlArr.append(source[a + 6: b - 1])
        return urlArr

    def getDate():
        return time.strftime("%Y%m%d", time.localtime())

    def getJPG(self, path, urlArr):
        print("ZQB Total " + str(len(urlArr)))
        for index in range(len(urlArr)):
            name = str(path + getDate()) + "_" + str(index + 1) + ".jpg"
            url = urlArr[index]
            req = requests.get(url)
            with open(name, "wb") as f:
                f.write(req.content)
            f.close()
            #print(name + " success")
        return True

    def JPG2PDF(self, path, num):
        for index in range(num):
            doc = fitz.open()
            img_file = path + getDate() + "_" + str(index+1) + ".jpg"
            imgdoc = fitz.open(img_file)
            pdfbytes = imgdoc.convert_to_pdf()
            pdf_name = path + getDate() + "_" + str(index+1) + ".pdf"
            imgpdf = fitz.open(pdf_name, pdfbytes)
            doc.insert_pdf(imgpdf)
            doc.save(path + "zqb_" + getDate() + "_" + str(index+1) + ".pdf")
            doc.close()
            os.remove(path + getDate() + "_" + str(index+1) + ".jpg")

    def getName(self, pid):
        u = "http://www.dooland.com/magazine/online_htm5.php?pid=" + str(pid)
        r = requests.get(url=u)
        res = r.content.decode("utf-8")
        s = res.find("<title>")
        e = res.find("电子杂志 - 读览天下")
        return res[s+7: e-1]

    def zqb(self, path, pid):
        key = self.getInkey(pid)
        dest = self.getDest(pid, key)
        source = self.bingo_decode(dest, key)
        urlArr = self.src2url(source)
        self.getJPG(path, urlArr)
        self.JPG2PDF(path, len(urlArr))
        print("ZQB Down Complete!")
        if mergePDF(len(urlArr), "zqb_", path, getDate()):
            name = self.getName(pid)
            os.rename(path+"zqb_"+getDate()+".pdf", path+name+".pdf")
            print("ZQB Merge Complete!")
            for index in range(len(urlArr)):
                os.remove(path+"zqb_"+getDate()+"_"+str(index+1)+".pdf")
            print("ZQB Delete Complete!")


def getDate():
    return time.strftime("%Y%m%d", time.localtime())

def downFile(url, name):
    req = requests.get(url)
    #print(req.content)
    with open(name, "wb") as f:
        f.write(req.content)
    f.close()
    return True

def mergePDF(length, type, path, date):
    file_merger = PyPDF2.PdfFileMerger(strict=False)
    #if type == "rmrb":
    for index in range(length):
        filename = path+type+str(date)+"_"+str(index+1)+".pdf"
        try:
            file_merger.append(filename)
        except:
            continue
    file_merger.write(path+type+date+".pdf")
    file_merger.close()
    return True

def CheckZQB():
    d = str(time.strftime("%m-%d", time.localtime()))
    u = "http://zqb.dooland.com/"
    r  =requests.get(u)
    rs = r.content.decode("utf-8")
    if rs.find(d) == -1:
        return "-1"
    else:
        s = rs.find(d)
        ss = rs.find("pid", s)
        return rs[ss+4: ss+12]

def CheckTTZB():
    day = str(time.strftime("%Y-%m-%d", time.localtime()))
    #day = "2021-12-10"
    param = "_VER=1.0&key=a7ff2586301b42eea962e9b9c8709689"
    sign = hashlib.md5(param.encode('utf-8'))
    d = "_VER=1.0&_SIGN="+sign.hexdigest().upper()
    u = "http://api.ttplus.cn/h5/pdf/recent"
    h = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
    r = requests.post(url=u, data=d, headers=h)
    rj = r.json()
    rday = rj["content"]["list"][0]["updatetime"]
    if rday == day:
        return rj["content"]["list"][0]["id"]
    else:
        return "-1"

def Auto():
    global RMRB_PARAM
    global BJYB_PARAM
    global ZQB_PARAM
    global TTZB_PARAM
    global DOWN_LIST
    week = time.strftime("%a", time.localtime())
    DOWN_LIST = [1, 2]
    if week == "Fri":
        ttzb = CheckTTZB()
        if ttzb == "-1":
            print("TTZB Not Exist")
        else:
            DOWN_LIST.append(3)
            TTZB_PARAM = ttzb
    elif week == "Thu":
        zqb = CheckZQB()
        if zqb == "-1":
            print("ZQB Not Exist")
        else:
            DOWN_LIST.append(4)
            ZQB_PARAM = zqb
    elif week == "Mon":
        ttzb = CheckTTZB()
        if ttzb == "-1":
            print("TTZB Not Exist")
        else:
            DOWN_LIST.append(3)
            TTZB_PARAM = ttzb

        zqb = CheckZQB()
        if zqb == "-1":
            print("ZQB Not Exist")
        else:
            DOWN_LIST.append(4)
            ZQB_PARAM = zqb
    RMRB_PARAM = 0
    BJYB_PARAM = 0

if __name__ == "__main__":

    AUTO = True
    PATH = "E:\\"
    DOWN_LIST = [1, 2]
    # 1-RMRB 2-BJYB 3-TTZB 4-ZQB
    RMRB_PARAM = 20211111
    #0-today, anyday(20200101--)
    BJYB_PARAM = 0
    # 0-today, anyday(20150101--)
    TTZB_CODE = "rayux~ddl|m~"
    TTZB_USERID = "userid"
    TTZB_COOKIE = "SESSION"
    TTZB_PARAM = "403636"
    # userid&cookie PARAM-id CODE-decrypt
    ZQB_COOKIE = "auth=XXXXXXXX"
    ZQB_UID = "12564116"
    ZQB_PARAM = "Mjk1MDQ"
    # UID-12564116-zqb PARAM-pid

    if AUTO:
        Auto()

    for index in range(len(DOWN_LIST)):
        NUM = DOWN_LIST[index]
        if NUM == 1:
            print("Select RMRB")
            rmrb = RMRB()
            rmrb.rmrb(PATH, RMRB_PARAM)
        elif NUM == 2:
            print("Select BJYB")
            bjyb = BJYB()
            bjyb.bjyb(PATH, BJYB_PARAM)
        elif NUM == 3:
            print("Select TTZB")
            ttzb = TTZB()
            ttzb.ttzb(PATH, TTZB_PARAM)
        elif NUM == 4:
            print("Select ZQB")
            zqb = ZQB()
            zqb.zqb(PATH, ZQB_PARAM)
