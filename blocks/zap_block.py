# coding=utf-8
import logging
import time
from pprint import pprint
from zapv2 import ZAPv2

from libs.cli_output import console


class ZapBlock:
    def __init__(self, api_key, local_proxy_ip='127.0.0.1', local_proxy_port='50501'):
        self.apiKey = api_key
        # MANDATORY. Define the listening address of ZAP instance
        self.localProxy = {"http": "http://" + local_proxy_ip + ":" + local_proxy_port,
                           "https": "http://" + local_proxy_ip + ":" + local_proxy_port}

        # MANDATORY. True to create another ZAP session (overwrite the former if the
        # same name already exists), False to use an existing one
        self.isNewSession = False
        # MANDATORY. ZAP Session name
        self.sessionName = 'SecBlocksSession'

        # Define the list of global exclude URL regular expressions. List can be empty.
        # The expressions must follow the java.util.regex.Pattern class syntax
        # The following example excludes every single URL except http://localhost:8081
        self.globalExcludeUrl = []

        # MANDATORY. Define if an outgoing proxy server is used
        self.useProxyChain = False
        # MANDATORY only if useProxyChain is True, ignored otherwise.
        # Outgoing proxy address and port
        self.proxyAddress = 'my.corp.proxy'
        self.proxyPort = '8080'
        # Define the addresses to skip in case useProxyChain is True. Ignored
        # otherwise. List can be empty.
        self.skipProxyAddresses = ('127.0.0.1;'
                                   'localhost')
        # MANDATORY only if useProxyChain is True. Ignored otherwise.
        # Define if proxy server needs authentication
        self.useProxyChainAuth = False
        # MANDATORY only if useProxyChainAuth is True. Ignored otherwise
        self.proxyUsername = ''
        self.proxyPassword = ''
        self.proxyRealm = ''

        # MANDATORY. Determine if a proxy script must be loaded. Proxy scripts are
        # executed for every request traversing ZAP
        self.useProxyScript = False
        # MANDATORY only if useProxyScript is True. Ignored otherwise
        self.proxyScriptName = 'proxyScript.js'
        # Script engine values: "Oracle Nashorn" for Javascript,
        # "jython" for python, "JSR 223 JRuby Engine" for ruby
        self.proxyScriptEngine = 'Oracle Nashorn'
        # Asolute local path
        self.proxyScriptFileName = '/zap/scripts/proxy/proxyScript.js'
        self.proxyScriptDescription = 'This is a description'

        # MANDATORY. Determine if context must be configured then used during scans.
        # You have to set this parameter to True if you want that ZAP performs scans
        # from the point of view of a specific user
        self.useContextForScan = False

        # MANDATORY only if useContextForScan is True. Ignored otherwise. Set value to
        # True to define a new context. Set value to False to use an existing one.
        self.defineNewContext = True
        # MANDATORY only if defineNewContext is True. Ignored otherwise
        self.contextName = 'WebGoat_script-based'
        # MANDATORY only if defineNewContext is False. Disregarded otherwise.
        # Corresponds to the ID of the context to use
        self.contextId = 0
        # Define Context Include URL regular expressions. Ignored if useContextForScan
        # is False. You have to put the URL you want to test in this list.
        self.contextIncludeURL = ['http://localhost:8081.*']
        # Define Context Exclude URL regular expressions. Ignored if useContextForScan
        # is False. List can be empty.
        self.contextExcludeURL = ['http://localhost:8081/WebGoat/j_spring_security_logout',
                                  'http://localhost:8081/WebGoat/logout.mvc']

        # MANDATORY only if useContextForScan is True. Ignored otherwise. Define the
        # session management method for the context. Possible values are:
        # "cookieBasedSessionManagement"; "httpAuthSessionManagement"
        self.sessionManagement = 'cookieBasedSessionManagement'

        # MANDATORY only if useContextForScan is True. Ignored otherwise. Define
        # authentication method for the context. Possible values are:
        # "manualAuthentication"; "scriptBasedAuthentication"; "httpAuthentication";
        # "formBasedAuthentication"
        self.authMethod = 'scriptBasedAuthentication'

        # MANDATORY only if authMethod is set to scriptBasedAuthentication.
        # Ignored otherwise
        self.authScriptName = 'TwoStepAuthentication.js'
        # Script engine values: Oracle Nashorn for Javascript
        # jython for python, JSR 223 JRuby Engine for ruby
        self.authScriptEngine = 'Oracle Nashorn'
        # Absolute local path
        self.authScriptFileName = '/zap/scripts/authentication/TwoStepAuthentication.js'
        self.authScriptDescription = 'This is a description'

        # MANDATORY only if useContextForScan is True. Ignored otherwise. Each
        # name/value pair of authParams are expected to be "x-www-form-urlencoded"
        # Here is an example for scriptBasedAuthentication method:
        self.authParams = ('scriptName=' + self.authScriptName + '&'
                                                                 'Submission Form URL=http://localhost:8081/WebGoat'
                                                                 '/j_spring_security_check& '
                                                                 'Username field=username&'
                                                                 'Password field=password&'
                                                                 'Target URL=http://localhost:8081/WebGoat/welcome.mvc')
        # Here is an example for formBasedAuthentication method:
        # authParams = ('loginUrl=http://localhost:8081/WebGoat/j_spring_security_check&'
        #              'loginRequestData=username%3D%7B%25username%25%7D%26'
        #              'password%3D%7B%25password%25%7D')
        # Here is an example for httpAuthentication method:
        # authParams = ('hostname=http://www.example.com&'
        #              'realm=CORP\\administrator&'
        #              'port=80')

        # MANDATORY only if useContextForScan is True. Ignored otherwise.
        # Set the value to True if a loggedin indicator must be used. False if it's a
        # logged out indicator that must be used
        self.isLoggedInIndicator = False
        # MANDATORY only if useContextForScan is True. Ignored otherwise.
        # Define either a loggedin or a loggedout indicator regular expression.
        # It allows ZAP to see if the user is always authenticated during scans.
        self.indicatorRegex = '\\QLocation: http://localhost:8081/WebGoat/login.mvc\\E'

        # MANDATORY only if useContextForScan is True. Ignored otherwise.
        # Set value to True to create new users, False otherwise
        self.createUser = True
        # MANDATORY only if createUser is True. Ignored otherwise. Define the list of
        # users, with name and credentials (in x-www-form-urlencoded format)
        # Here is an example with the script NashornTwoStepAuthentication.js:
        self.userList = [
            {'name': 'guest', 'credentials': 'Username=guest&Password=guest'},
            {'name': 'webgoat', 'credentials': 'Username=webgoat&Password=webgoat'}
        ]
        # Here is an example with formBasedAuthentication:
        # userList = [
        #    {'name': 'guest', 'credentials': 'username=guest&password=guest'},
        #    {'name': 'webgoat', 'credentials': 'username=webgoat&password=webgoat'}
        # ]

        # MANDATORY only if useContextForScan is True. Ignored otherwise. List can be
        # empty. Define the userid list. Created users will be added to this list later
        self.userIdList = []

        # MANDATORY. Define the target site to test
        # self.target = 'http://127.0.0.1:8081/Main'

        # You can specify other URL in order to help ZAP discover more site locations
        # List can be empty
        self.applicationURL = []

        # MANDATORY. Set value to True if you want to customize and use a scan policy
        self.useScanPolicy = False
        # MANDATORY only if useScanPolicy is True. Ignored otherwise. Set a policy name
        self.scanPolicyName = 'SQL Injection and XSS'
        # MANDATORY only if useScanPolicy is True. Ignored otherwise.
        # Set value to True to disable all scan types except the ones set in ascanIds,
        # False to enable all scan types except the ones set in ascanIds..
        self.isWhiteListPolicy = False
        # MANDATORY only if useScanPolicy is True. Ignored otherwise. Set the scan IDs
        # to use with the policy. Other scan types will be disabled if
        # isWhiteListPolicy is True, enabled if isWhiteListPolicy is False.
        # Use zap.ascan.scanners() to list all ascan IDs.
        # In the example bellow, the first line corresponds to SQL Injection scan IDs,
        # the second line corresponds to some XSS scan IDs
        self.ascanIds = []
        # MANDATORY only if useScanPolicy is True. Ignored otherwise. Set the alert
        # Threshold and the attack strength of enabled active scans.
        # Currently, possible values are:
        # Low, Medium and High for alert Threshold
        # Low, Medium, High and Insane for attack strength
        self.alertThreshold = 'Medium'
        self.attackStrength = 'Low'

        # MANDATORY. Set True to use Ajax Spider, False otherwise.
        self.useAjaxSpider = True

        # MANDATORY. Set True to shutdown ZAP once finished, False otherwise
        self.shutdownOnceFinished = False

        # Connect ZAP API client to the listening address of ZAP instance
        self.zap = ZAPv2(proxies=self.localProxy, apikey=self.apiKey)
        # Start the ZAP session
        self.core = self.zap.core
        # MANDATORY. Define the target site to test
        self.target = ''
        pass

    # 单一扫描
    def single_scan(self, target_url):
        # Connect ZAP API client to the listening address of ZAP instance
        zap = self.zap

        # Start the ZAP session
        core = self.core

        # MANDATORY. Define the target site to test
        self.target = target_url

        if self.isNewSession:
            pprint('Create ZAP session: ' + self.sessionName + ' -> ' +
                   core.new_session(name=self.sessionName, overwrite=True))
        else:
            pprint('Load ZAP session: ' + self.sessionName + ' -> ' +
                   core.load_session(name=self.sessionName))

        # Configure ZAP global Exclude URL option
        print('Add Global Exclude URL regular expressions:')
        for regex in self.globalExcludeUrl:
            pprint(regex + ' ->' + core.exclude_from_proxy(regex=regex))

        # Configure ZAP outgoing proxy server connection option
        pprint('Enable outgoing proxy chain: ' + str(self.useProxyChain) + ' -> ' +
               core.set_option_use_proxy_chain(boolean=self.useProxyChain))
        if self.useProxyChain:
            pprint('Set outgoing proxy name: ' + self.proxyAddress + ' -> ' +
                   core.set_option_proxy_chain_name(string=self.proxyAddress))
            pprint('Set outgoing proxy port: ' + self.proxyPort + ' -> ' +
                   core.set_option_proxy_chain_port(integer=self.proxyPort))
            pprint('Skip names for outgoing proxy: ' + self.skipProxyAddresses + ' -> ' +
                   core.set_option_proxy_chain_skip_name(string=self.skipProxyAddresses))

            # Configure ZAP outgoing proxy server authentication
            pprint('Set outgoing proxy chain authentication: ' +
                   str(self.useProxyChainAuth) + ' -> ' +
                   core.set_option_use_proxy_chain_auth(boolean=self.useProxyChainAuth))
            if self.useProxyChainAuth:
                pprint('Set outgoing proxy username -> ' +
                       core.set_option_proxy_chain_user_name(string=self.proxyUsername))
                pprint('Set outgoing proxy password -> ' +
                       core.set_option_proxy_chain_password(string=self.proxyPassword))
                pprint('Set outgoing proxy realm: ' + self.proxyRealm + ' -> ' +
                       core.set_option_proxy_chain_realm(string=self.proxyRealm))

        if self.useProxyScript:
            script = zap.script
            script.remove(scriptname=self.proxyScriptName)
            pprint('Load proxy script: ' + self.proxyScriptName + ' -> ' +
                   script.load(scriptname=self.proxyScriptName, scripttype='proxy',
                               scriptengine=self.proxyScriptEngine,
                               filename=self.proxyScriptFileName,
                               scriptdescription=self.proxyScriptDescription))
            pprint('Enable proxy script: ' + self.proxyScriptName + ' -> ' +
                   script.enable(scriptname=self.proxyScriptName))

        if self.useContextForScan:
            # Define the ZAP context
            context = zap.context
            if self.defineNewContext:
                self.contextId = context.new_context(contextname=self.contextName)
            pprint('Use context ID: ' + self.contextId)

            # Include URL in the context
            print('Include URL in context:')
            for url in self.contextIncludeURL:
                pprint(url + ' -> ' +
                       context.include_in_context(contextname=self.contextName,
                                                  regex=url))

            # Exclude URL in the context
            print('Exclude URL from context:')
            for url in self.contextExcludeURL:
                pprint(url + ' -> ' +
                       context.exclude_from_context(contextname=self.contextName,
                                                    regex=url))

            # Setup session management for the context.
            # There is no methodconfigparams to provide for both current methods
            pprint('Set session management method: ' + self.sessionManagement + ' -> ' +
                   zap.sessionManagement.set_session_management_method(
                       contextid=self.contextId, methodname=self.sessionManagement,
                       methodconfigparams=None))

            # In case we use the scriptBasedAuthentication method, load the script
            if self.authMethod == 'scriptBasedAuthentication':
                script = zap.script
                script.remove(scriptname=self.authScriptName)
                pprint('Load script: ' + self.authScriptName + ' -> ' +
                       script.load(scriptname=self.authScriptName,
                                   scripttype='authentication',
                                   scriptengine=self.authScriptEngine,
                                   filename=self.authScriptFileName,
                                   scriptdescription=self.authScriptDescription))

            # Define an authentication method with parameters for the context
            auth = zap.authentication
            pprint('Set authentication method: ' + self.authMethod + ' -> ' +
                   auth.set_authentication_method(contextid=self.contextId,
                                                  authmethodname=self.authMethod,
                                                  authmethodconfigparams=self.authParams))
            # Define either a loggedin indicator or a loggedout indicator regexp
            # It allows ZAP to see if the user is always authenticated during scans
            if self.isLoggedInIndicator:
                pprint('Define Loggedin indicator: ' + self.indicatorRegex + ' -> ' +
                       auth.set_logged_in_indicator(contextid=self.contextId,
                                                    loggedinindicatorregex=self.indicatorRegex))
            else:
                pprint('Define Loggedout indicator: ' + self.indicatorRegex + ' -> ' +
                       auth.set_logged_out_indicator(contextid=self.contextId,
                                                     loggedoutindicatorregex=self.indicatorRegex))

            # Define the users
            users = zap.users
            if self.createUser:
                for user in self.userList:
                    userName = user.get('name')
                    print('Create user ' + userName + ':')
                    userId = users.new_user(contextid=self.contextId, name=userName)
                    self.userIdList.append(userId)
                    pprint('User ID: ' + userId + '; username -> ' +
                           users.set_user_name(contextid=self.contextId, userid=userId,
                                               name=userName) +
                           '; credentials -> ' +
                           users.set_authentication_credentials(contextid=self.contextId,
                                                                userid=userId,
                                                                authcredentialsconfigparams=user.get('credentials')) +
                           '; enabled -> ' +
                           users.set_user_enabled(contextid=self.contextId, userid=userId,
                                                  enabled=True))

        # Enable all passive scanners (it's possible to do a more specific policy by
        # setting needed scan ID: Use zap.pscan.scanners() to list all passive scanner
        # IDs, then use zap.scan.enable_scanners(ids) to enable what you want
        pprint('Enable all passive scanners -> ' +
               zap.pscan.enable_all_scanners())

        ascan = zap.ascan
        # Define if a new scan policy is used
        if self.useScanPolicy:
            ascan.remove_scan_policy(scanpolicyname=self.scanPolicyName)
            pprint('Add scan policy ' + self.scanPolicyName + ' -> ' +
                   ascan.add_scan_policy(scanpolicyname=self.scanPolicyName))
            for policyId in range(0, 5):
                # Set alert Threshold for all scans
                ascan.set_policy_alert_threshold(id=policyId,
                                                 alertthreshold=self.alertThreshold,
                                                 scanpolicyname=self.scanPolicyName)
                # Set attack strength for all scans
                ascan.set_policy_attack_strength(id=policyId,
                                                 attackstrength=self.attackStrength,
                                                 scanpolicyname=self.scanPolicyName)
            if self.isWhiteListPolicy:
                # Disable all active scanners in order to enable only what you need
                pprint('Disable all scanners -> ' +
                       ascan.disable_all_scanners(scanpolicyname=self.scanPolicyName))
                # Enable some active scanners
                pprint('Enable given scan IDs -> ' +
                       ascan.enable_scanners(ids=self.ascanIds,
                                             scanpolicyname=self.scanPolicyName))
            else:
                # Enable all active scanners
                pprint('Enable all scanners -> ' +
                       ascan.enable_all_scanners(scanpolicyname=self.scanPolicyName))
                # Disable some active scanners
                pprint('Disable given scan IDs -> ' +
                       ascan.disable_scanners(ids=self.ascanIds,
                                              scanpolicyname=self.scanPolicyName))
        else:
            print('No custom policy used for scan')
            self.scanPolicyName = None

        # Open URL inside ZAP
        pprint('Access target URL ' + self.target)
        core.access_url(url=self.target, followredirects=True)
        for url in self.applicationURL:
            pprint('Access URL ' + url)
            core.access_url(url=url, followredirects=True)
        # Give the sites tree a chance to get updated
        time.sleep(2)

        # Launch Spider, Ajax Spider (if useAjaxSpider is set to true) and
        # Active scans, with a context and users or not
        forcedUser = zap.forcedUser
        spider = zap.spider
        ajax = zap.ajaxSpider
        # scanId = 0
        print('Starting Scans on target: ' + self.target)
        if self.useContextForScan:
            for userId in self.userIdList:
                print('Starting scans with User ID: ' + userId)

                # Spider the target and recursively scan every site node found
                scanId = spider.scan_as_user(contextid=self.contextId, userid=userId,
                                             url=self.target, maxchildren=None, recurse=True, subtreeonly=None)
                print('Start Spider scan with user ID: ' + userId +
                      '. Scan ID equals: ' + scanId)
                # Give the spider a chance to start
                time.sleep(2)
                while int(spider.status(scanId)) < 100:
                    print('Spider progress: ' + spider.status(scanId) + '%')
                    time.sleep(2)
                print('Spider scan for user ID ' + userId + ' completed')

                if self.useAjaxSpider:
                    # Prepare Ajax Spider scan
                    pprint('Set forced user mode enabled -> ' +
                           forcedUser.set_forced_user_mode_enabled(boolean=True))
                    pprint('Set user ID: ' + userId + ' for forced user mode -> ' +
                           forcedUser.set_forced_user(contextid=self.contextId,
                                                      userid=userId))
                    # Ajax Spider the target URL
                    pprint('Ajax Spider the target with user ID: ' + userId + ' -> ' +
                           ajax.scan(url=self.target, inscope=None))
                    # Give the Ajax spider a chance to start
                    time.sleep(10)
                    while ajax.status != 'stopped':
                        print('Ajax Spider is ' + ajax.status)
                        time.sleep(5)
                    for url in self.applicationURL:
                        # Ajax Spider every url configured
                        pprint('Ajax Spider the URL: ' + url + ' with user ID: ' +
                               userId + ' -> ' +
                               ajax.scan(url=url, inscope=None))
                        # Give the Ajax spider a chance to start
                        time.sleep(10)
                        while ajax.status != 'stopped':
                            print('Ajax Spider is ' + ajax.status)
                            time.sleep(5)
                    pprint('Set forced user mode disabled -> ' +
                           forcedUser.set_forced_user_mode_enabled(boolean=False))
                    print('Ajax Spider scan for user ID ' + userId + ' completed')

                # Launch Active Scan with the configured policy on the target url
                # and recursively scan every site node
                scanId = ascan.scan_as_user(url=self.target, contextid=self.contextId,
                                            userid=userId, recurse=True, scanpolicyname=self.scanPolicyName,
                                            method=None, postdata=True)
                print('Start Active Scan with user ID: ' + userId +
                      '. Scan ID equals: ' + scanId)
                # Give the scanner a chance to start
                time.sleep(2)
                while int(ascan.status(scanId)) < 100:
                    print('Active Scan progress: ' + ascan.status(scanId) + '%')
                    time.sleep(2)
                print('Active Scan for user ID ' + userId + ' completed')

        else:
            # Spider the target and recursively scan every site node found
            scanId = spider.scan(url=self.target, maxchildren=None, recurse=True,
                                 contextname=None, subtreeonly=None)
            print('Scan ID equals ' + scanId)
            # Give the Spider a chance to start
            time.sleep(2)
            while int(spider.status(scanId)) < 100:
                print('Spider progress ' + spider.status(scanId) + '%')
                time.sleep(2)
            print('Spider scan completed')

            if self.useAjaxSpider:
                # Ajax Spider the target URL
                pprint('Start Ajax Spider -> ' + ajax.scan(url=self.target, inscope=None))
                # Give the Ajax spider a chance to start
                time.sleep(10)
                while ajax.status != 'stopped':
                    print('Ajax Spider is ' + ajax.status)
                    time.sleep(5)
                for url in self.applicationURL:
                    # Ajax Spider every url configured
                    pprint('Ajax Spider the URL: ' + url + ' -> ' +
                           ajax.scan(url=url, inscope=None))
                    # Give the Ajax spider a chance to start
                    time.sleep(10)
                    while ajax.status != 'stopped':
                        print('Ajax Spider is ' + ajax.status)
                        time.sleep(5)
                print('Ajax Spider scan completed')

            try:
                # Launch Active scan with the configured policy on the target url and
                # recursively scan every site node
                scanId = zap.ascan.scan(url=self.target, recurse=True, inscopeonly=None,
                                        scanpolicyname=self.scanPolicyName, method=None, postdata=True,
                                        apikey=self.apiKey)
                print('Start Active scan. Scan ID equals ' + scanId)

                if 'url_not_found' == str(scanId):
                    console(__name__, "abort Active Scan")
                    pass
                else:
                    while int(ascan.status(scanId)) < 100:
                        print('Active Scan progress: ' + ascan.status(scanId) + '%')
                        time.sleep(5)
                    print('Active Scan completed')

            except Exception as e:
                logging.exception(e)
                console(__name__, "Active Scan exception", str(e))

        # Give the passive scanner a chance to finish
        time.sleep(5)

        # If you want to retrieve alerts:
        # str_alerts = zap.core.alerts(baseurl=self.target, start=None, count=None)
        # pprint(str_alerts)
        # To retrieve ZAP report in XML or HTML format
        # print('XML report')
        # str_xml = core.xmlreport()
        # pprint(str_xml)
        # print('HTML report:')
        str_html = core.htmlreport()
        # pprint(str_html)
        if self.shutdownOnceFinished:
            # Shutdown ZAP once finished
            pprint('Shutdown ZAP -> ' + core.shutdown())

        return str_html

    # 关闭zap主程序
    def shutdown(self):
        # Shutdown ZAP once finished
        pprint('Shutdown ZAP -> ' + self.core.shutdown())
