# -*- coding: utf-8 -*-

import re
from datetime import datetime
from enum import Enum
from utils import nested_set


def nbu2list(nbufile):
    """
    Converts every line in a file containing VMSG to be key:value pair and returns list where every element is a
    multiline string with fixed VMSG.
    :param nbufile: (str) path to .nbu file containing message backup
    :return: (list) of (str) contaning fixed VMSG
    """
    vmessages = []
    with open(nbufile, encoding="utf_16le", errors="ignore") as f:
        in_vmsg = False
        in_vbody = False
        msg = ""
        content = ""

        for line in f:
            if "BEGIN:VMSG" in line:
                in_vmsg = True
                line = "BEGIN:VMSG\n"
            if "BEGIN:VBODY" in line:
                in_vbody = True

            if in_vbody:
                if "Date" in line:
                    continue
                if "VBODY" not in line:
                    content += line.replace("\n", "")
                    continue
                if "END:VBODY" in line:
                    line = "CONTENT:{0}\n".format(content)
                    content = ""
                    in_vbody = False

            if in_vmsg:
                msg += line
            if "END:VMSG" in line:
                in_vmsg = False
                vmessages.append(msg)
                msg = ""
    return vmessages


class BaseMessage:
    class MessageType(Enum):
        SENT = 0
        RECEIVED = 1


class Message(BaseMessage):
    def __init__(self, vmsg):
        """
        :param vmsg: multiline (str) containing fixed VMSG
        """
        dict_ = Message.vmsg2dict(vmsg)

        if dict_["VMSG"]["X-MESSAGE-TYPE"] == "DELIVER":
            self.type = Message.MessageType.RECEIVED
            self.content = dict_["VMSG"]["VENV"]["VBODY"]["CONTENT"]
            self.phonenum = dict_["VMSG"]["VCARD"]["TEL"]

        if dict_["VMSG"]["X-MESSAGE-TYPE"] == "SUBMIT":
            self.type = Message.MessageType.SENT
            self.content = dict_["VMSG"]["VENV"]["VENV"]["VBODY"]["CONTENT"]
            self.phonenum = dict_["VMSG"]["VENV"]["VCARD"]["TEL"]

        self.date = datetime.strptime(dict_["VMSG"]["X-NOK-DT"].replace("\n", ""), "%Y%m%dT%H%M%SZ")

    @staticmethod
    def vmsg2dict(vmsg):
        """
        Converts fixed VMSG to dict.
        :param vmsg: multiline (str) with fixed VMSG
        :return: (dict)
        """
        dict_ = {}
        metas = []

        for line in vmsg.splitlines():
            splt = line.split(":", 1)
            key = splt[0]
            value = splt[1]

            if key == "BEGIN":
                metas.append(value)
                continue
            if key == "END":
                metas.remove(value)
                continue
            nested_set(dict_, metas + [key], value)

        return dict_


class Analyzer(BaseMessage):
    def __init__(self, nbufile):
        """
        :param nbufile: (str) path to .nbu file containing message backup
        """
        vmessages = nbu2list(nbufile)
        self.sent = []
        self.received = []

        for vmsg in vmessages:
            msg = Message(vmsg)
            self._which(msg.type).append(msg)

    def _which(self, type_):
        messages = []
        if type_ == Message.MessageType.RECEIVED:
            messages = self.received
        if type_ == Message.MessageType.SENT:
            messages = self.sent
        return messages

    def search_regex(self, type_, regex, case_sensitive=False, datefmt="%Y-%m"):
        """
        Searches for regex in given type_ of message and returns results grouped in datetime buckets.
        :param type_: (BaseMessage.Type)
        :param regex: raw (str)
        :param case_sensitive: (bool)
        :param datefmt: (str) which defines bucket size; follows strftime standard
        :return: (dict)
        """
        results = {}
        regex_flags = re.IGNORECASE if not case_sensitive else 0

        for msg in self._which(type_):
            if not msg.date.strftime(datefmt) in results:
                results[msg.date.strftime(datefmt)] = {"count": 0, "messages": []}
            rem = re.findall(regex, msg.content, regex_flags)
            if len(rem) > 0:
                results[msg.date.strftime(datefmt)]["count"] += len(rem)
                results[msg.date.strftime(datefmt)]["messages"].append(msg)
        return results

    def search_phone(self, type_, phonenum):
        results = []
        for msg in self._which(type_):
            if phonenum in msg.phonenum:
                results.append(msg)
        return results
