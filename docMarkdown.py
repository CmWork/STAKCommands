import fnmatch, os, sys
from bs4 import BeautifulSoup as bs
import json
from jsonschema import Draft4Validator
import re
from collections import OrderedDict

class FileParser:
    def __init__(self):
        self.PACKAGE_PATH = './testmethodology/Methodology/Packages/'
        self.TEMPLATE_PATH = './testmethodology/Methodology/Templates/'
        self.SCRIPTS_PATH = './testmethodology/Methodology/Scripts/'
        self.dmFileList = list()
        self.seqFileList = list()
        self.tempFileList = list()
        self.getFileList()

        '''
        self.cmdMethDict
        {
            <shortCmdName>: set(<methodology>)
        }
        '''
        self.cmdMethDict = OrderedDict()
        for seq in self.seqFileList:
            self.parseSequencer(seq)
        # print self.cmdMethDict

        '''
        self.cmdDict
        {
            # cmdDict
            <basename>: {
                #cmdInfoDict
                <cmdName>: {
                    'package': <methodology package>,
                    'displayName': <display name>,
                    'description': <description>,
                    'meths': <meths cmd is used in>,
                    # propsDict
                    'properties': {
                        # propDict
                        <propName>: {
                            'category': <category>,
                            'displayName': <display name>,
                            'type': <type>,
                            'default': <default value if not JSON>,
                            'enums': <optional enum values>,
                            'description': <description>,
                            'json': <json schema if not default value>
                        }
                    }
                    # addInfoDict
                    'addedInfo': {
                        'json': list(<json examples>),
                        'tag': list(<html tags>)
                    }
                }
            }
        }
        '''
        # The cmd dict to be ref'd by module...
        self.cmdDict = OrderedDict()
        # Cross ref cmd dict to ref cmd info by fq cmd name only...
        self.crefDict = {}
        for dm in self.dmFileList:
            basename = os.path.basename(dm)
            self.cmdDict[basename] = self.parseDataModel(dm, self.cmdMethDict)
        #print self.cmdDict

        '''
        self.tempDict
        {
            # tempDict
            <basename>: {
                # tagDict
                'xml': {
                    <tagid>: {
                        'name': <tag name>,
                        'parent': <parent tag if tag is used>,
                        'info': <notes about how to use the tag>
                    }
                }
                'json': FIX_ME
            }
        }
        '''
        self.tempDict = OrderedDict()
        for temp in self.tempFileList:
            basename = os.path.basename(temp)
            self.tempDict[basename] = self.parseTemplate(temp, basename)

    def getData(self):
        return (self.cmdDict, self.tempDict, self.crefDict)

    def getFiles(self, isSeq, path, fileFilters):
        matches = list()
        for root, dirnames, filenames in os.walk(path):
            for fileFilter in fileFilters.split(','):
                for filename in fnmatch.filter(filenames, fileFilter):
                    if isSeq:
                        meta = os.path.join(root, 'meta.txml')
                        seq = os.path.join(root, filename)
                        methFile = (seq, meta)
                    else:
                        methFile = os.path.join(root, filename)
                    matches.append(methFile)
            if not isSeq:
                break
        return matches

    def getFileList(self):
        self.dmFileList = self.getFiles(False, './', '*.xml')
        self.seqFileList = self.getFiles(True, self.PACKAGE_PATH, 'sequencer.xml')
        self.tempFileList = self.getFiles(False, self.TEMPLATE_PATH, '*.xml,*.json')

    def parseDataModel(self, filename, cmdMethDict):
        cmdDict = OrderedDict()
        try:
            f = open(filename, 'r')
        except:
            print 'ERROR: ' + filename + ': does not exist'
            return
        soup = bs(f.read(), ['lxml', 'xml'])

        # Find meta
        meta = soup.find('meta')
        fqPackage = meta['package'].lower()
        package = '.'.join(meta['package'].split('.')[1:]).upper()

        # Find class
        classes = soup.find_all('class')
        for stc_class in classes:
            try:
                cmdName = str(stc_class['name'])
                    
                cmdInfoDict = OrderedDict()
                cmdInfoDict['hidden'] = stc_class.has_key('isInternal') and stc_class['isInternal'] == 'true'
                cmdInfoDict['package'] = package
                cmdInfoDict['displayName'] = str(stc_class['displayName'])
                cmdInfoDict['baseClass'] = str(stc_class['baseClass']) \
                    if stc_class.has_key('baseClass') else None

                cmdInfoDict['description'] = 'MISSING DESCRIPTION'
                stc_att = stc_class.find('attribute', type='framework.CommandDescription')
                if stc_att is not None:
                    cmdInfoDict['description'] = str(stc_att['value'])
                
                # Command in Meths
                cmdInfoDict['meths'] = None
                if cmdName in cmdMethDict.keys():
                    cmdInfoDict['meths'] = cmdMethDict[cmdName]

                enumDict = self.parseEnums(stc_class)

                props = stc_class.find_all('property')
                cmdInfoDict['properties'] = self.parseProps(cmdName, props, enumDict)
                cmdInfoDict['addedInfo'] = self.parseAdditionalComments(stc_class)
                cmdDict[cmdName] = cmdInfoDict
                # Use a fq cmd name as key for easy ref using base class attribute value...
                self.crefDict[fqPackage + '.' + cmdName] = cmdInfoDict
            except KeyError as e:
                print cmdName + ' has no key: ' + e.message
        return cmdDict
        f.close()

    def parseEnums(self, cmdClass):
        enumDict = OrderedDict()
        enums = cmdClass.find_all('enumeration')
        for enum in enums:
            enumItemList = list()
            enumName = enum['name']
            enumList = enum.find_all('enum')
            for enumItem in enumList:
                enumItemList.append((enumItem['name'], enumItem['value']))
            enumDict[enumName] = enumItemList
        return enumDict

    def parseProps(self, cmdName, propertyList, enumDict):
        propsDict = OrderedDict()
        for prop in propertyList:
            propName = str(prop['name'])
            try:
                propDict = OrderedDict()
                propDict['category'] = str(prop['category'])
                propDict['displayName'] = str(prop['displayName'])
                propDict['type'] = str(prop['type'])
                propDict['default'] = str(prop['default'])
                propDict['enums'] = None
                enumRef = prop.find('enumerationRef')
                if enumRef is not None:
                    enumName = enumRef['ref']
                    if enumName in enumDict:
                        propDict['enums'] = (enumName, enumDict[enumName])
                    else:
                        propDict['enums'] = (enumName, )

                propDict['description'] = 'MISSING DESCRIPTION'
                stc_att = prop.find('attribute', type='framework.PropertyDescription')
                if stc_att is not None:
                    propDict['description'] = str(stc_att['value'])

                # State: JSON Schema
                propDict['json'] = None
                if prop['category'] == 'state' and prop['default'] != '':
                    try:
                        Draft4Validator.check_schema(json.loads(prop['default']))
                        propDict['json'] = str(prop['default'])
                        propDict['default'] = None
                    except:
                        propDict['json'] = None
                propsDict[propName] = propDict
            except KeyError as e:
                print cmdName + ':' + propName + ' has no key: ' + e.message
        return propsDict

    def parseSequencer(self, filename):
        try:
            seq = open(filename[0], 'r')
            meta = open(filename[1], 'r')
        except:
            print 'ERROR: ' + filename[0] + ' or ' + filename[1] + ': does not exist'
            return

        s_meta = bs(meta.read(), ['lxml', 'xml'])
        metaInfo = s_meta.find('testInfo')
        meth = (str(metaInfo['displayName']), str(metaInfo['description']))

        s_seq = bs(seq.read(), ['lxml', 'xml'])
        cmds = s_seq.find_all(re.compile('(\w*)Command$'))
        for cmd in cmds:
            cmdNameSplit = cmd.name.split('.')
            shortCmdName = cmdNameSplit[len(cmdNameSplit)-1]
            if shortCmdName not in self.cmdMethDict.keys():
                self.cmdMethDict[shortCmdName] = set()
            self.cmdMethDict[shortCmdName].add(meth)

        seq.close()
        meta.close()

    '''
There are two ways to add comments to your commands. The first is using the
SAMPLE_JSON comment, and the second is using the standard NOTES comment.

<!-- SAMPLE_JSON: 
You can add any discussion here that you wish. When you want to present JSON
sample, you can present it in fixed font box format by indenting the text as
shown here:

    {
        "here": "there"
    }

You can add more notes and you can even use {braces} in your discussion text.
And you can have as many samples (in fixed font boxes) as you wish in a single
SAMPLE_JSON comment. The only advantage of using SAMPLE_JSON rather than NOTES
is that the entire comment is presented in the JSON Sample section at the bottom.
-->


<!-- NOTES:
You can add any comments you wish to have appear directly under the command
name. This is typically where a discussion of what the command does, when
it should be used, and nuances regarding its use is presented.

This is some discussion text here. While there is a JSON Sample section
and a SAMPLE_JSON comment key that goes with it, you can add small JSON
samples to your discussion and present them in fixed font boxes by simply
indenting the text you want boxed.

    {
        "json": "sample",
        "this": "is indented"
    }

You can add as much discussion as you wish and you can go between discussion
and fixed font boxes as often as you wish. You can create a fixed font box in
your notes for any kind of sample where you want to emphasize verbatim text.

    <xml sample="can be fixed font boxed as well if indented"/>

You can also add images... <img src='somesource' /> or other
<br><br><h3>HTML text</h3> that you want within the comment. What you cannot
add inside the XML comment is an XML (HTML) comment (for obvious reasons).
        -->
    '''
    def parseAdditionalComments(self, cmdInfo):
        addInfoDict = OrderedDict()
        sampJsons = re.findall('<!-- SAMPLE_JSON:([\s\S]+?)-->', str(cmdInfo))
        for m in sampJsons:
            if 'json' not in addInfoDict:
                addInfoDict['json'] = list()
            addInfoDict['json'].append(m)

        tag_ex = re.findall('.*<!-- NOTES:([\s\S]+?)-->', str(cmdInfo))
        for m in tag_ex:
            if 'tag' not in addInfoDict:
                addInfoDict['tag'] = list()
            addInfoDict['tag'].append(m.strip())

        return addInfoDict

    def parseTemplate(self, filename, basename):
        tempDict = OrderedDict()
        try:
            f = open(filename, 'r')
        except:
            print 'ERROR: ' + filename + ': does not exist'
            return
        ext = basename.split('.')[1]
        if ext == 'xml':
            soup = bs(f.read(), ['lxml', 'xml'])
            tempDict['xml'] = self.parseXmlTemplate(filename, soup)
            tempDict['map'] = self.createMap(soup, tempDict['xml'])
            return tempDict
        elif ext == 'json':
            tempDict['json'] = ''
            print basename + ": THIS FILE IS JSON"
            return tempDict
        else:
            print 'ERROR: ' + basename + ' has an unknown template extension'

    '''
<Description>
Use the template's description node to add in information regarding the
template file.

    If you need to box a fixed font section of comments, you simply
    need to indent.

You can switch between box and discussion as you wish.
<ttSomeTagName>
This text appears under the section for ttSomeTagName.

    You can box here as well simply by indenting.

And of course switch back and forth as you require.
</ttSomeTagName>
anything in between tags is not captured or used in any way.
<ttAnotherTagName>
You can have as many tag descriptions as you wish.
</ttAnotherTagName>
More text for the description of the template file...
</Description>
    '''

    def findTagFromClass(self, dic, classname):
        for k,v in dic.iteritems():
            if 'parentTag' in v and v['parentTag'] == classname:
                return v['name']
        return None

    def parseXmlTemplate(self, filename, soup):
        tagDict = OrderedDict()
        self.parseUserTagRelation(soup, tagDict)
        self.parseTagName(soup, tagDict)
        self.parseDesc(soup, tagDict)

        # Unused tags
        for tagid in tagDict.keys():
            if 'parent' not in tagDict[tagid]:
                tagname = 'NO_NAME'
                if 'name' in tagDict[tagid]:
                    tagname = tagDict[tagid]['name']
                print 'ERROR: ' + filename + ' ' + tagname + ' (' + tagid + ') is not used'
                if tagid != 'names' and tagid != 'info':
                    tagDict.pop(tagid)
        return tagDict

    def parseTagName(self, soup, tagDict):
        tagObjs = soup.find_all('Tag')
        tagDict['names'] = {}
        for tag in tagObjs:
            tagid = tag['id']
            if tagid in tagDict.keys():
                tagDict[tagid]['name'] = tag['Name']
                tagDict['names'][tag['Name']] = tagid

    def parseUserTagRelation(self, soup, tagDict):
        # Find User Tag Relation
        relations = soup.find_all('Relation', attrs={'type': 'UserTag'})
        for rel in relations:
            tagid = rel['target']
            if tagid not in tagDict.keys():
                # Doesn't seem like this needs to be an OrderedDict
                tagDict[tagid] = OrderedDict()
            else:
                if tagid == 'info' or tagid == 'names':
                    continue
                tagDict[tagid]['parent'] = rel.parent
                tagDict[tagid]['parentTag'] = rel.parent.name

    def parseDesc(self, soup, tagDict):
        for info in re.findall('<Description>([^<]*)(<[\s\S]*>)*([^<]*)<\/Description>', str(soup)):
            tagDict['info'] = str(info[0]) + '\n' + str(info[2])
            for tags in re.findall('(<([\s\S]+?)>([\s\S]+?)</([\s\S]+?)>)', str(info[1])):
                if tags[1] in tagDict['names'].keys():
                    tagDict[tagDict['names'][tags[1]]]['info'] = tags[2]

    def xmlTree(self, xmlSoup, tagDict):
        jDict = dict()
        cList = list()

        name = xmlSoup.name
        tag = self.findTagFromClass(tagDict, name)
        if tag:
            name += ':' + tag
            jDict['url'] = '#' + tag
        jDict['name'] = name
        jDict['parent'] = xmlSoup.parent.name

        for childXml in xmlSoup.children:
            if not childXml.name or childXml.name in ['Relation', 'Tags', 'Tag']:
                continue

            childDict = self.xmlTree(childXml, tagDict)
            if childDict:
                cList.append(childDict)

        if cList:
            jDict['children'] = cList
        return jDict

    def createMap(self, soup, tagDict):
        parXml = soup.find('DataModelXml')
        sysXml = parXml.find('StcSystem')
        jDict = self.xmlTree(sysXml, tagDict)
        return jDict

class MarkdownProducer:
    def __init__(self, inDict, markdownPath):
        self.cmdDict = inDict[0]
        self.tempDict = inDict[1]
        self.crefDict = inDict[2]
        self.path = markdownPath

        # If more parameters are needed this should be moved to a template file
        yamlTemp = ("site_name: Spirent Methodology Infrastructure\n"
                    "theme: readthedocs\n\n"
                    "pages:\n"
                    "- Home: 'index.md'\n"
                    "- Commands:\n")

        # Command Section
        for lowerName, refName in sorted((k.lower(), k) for k in self.cmdDict.keys()):
            inDict = self.cmdDict[refName]

            # remove if needing to support non-methodology files
            if 'methodology' in refName:
                yamlTemp = yamlTemp + '    ' + self.generateCmdListMarkdown(refName, inDict) + '\n'

        # Template Section
        yamlTemp = yamlTemp + "- Templates:\n"
        for refName in self.tempDict.keys():
            inDict = self.tempDict[refName]

            # remove when/if json templates are supported
            if 'xml' in inDict:
                yamlTemp = yamlTemp + '    ' + self.generateTemplateListMarkdown(refName, inDict) + '\n'

        # Write YAML
        ypath = os.path.join(self.path, '../mkdocs.yml')
        print ypath
        y = open(ypath, 'w+')
        y.write(yamlTemp)

    def makeFilePath(self, refName, refType):
        refPath = refName.split('.')[0]
        subPath = refType + '/' + refPath + '.md'

        fpath = os.path.join(self.path, subPath)
        if not os.path.exists(os.path.dirname(fpath)):
            os.makedirs(os.path.dirname(fpath))
        f = open(fpath, 'w+')
        return (f, subPath)

    def makeMapPath(self, refName, refType):
        refPath = refName.split('.')[0]
        subPath = refType + '/' + refPath + '/dmMap.jtree'

        sitePath = os.path.join(os.path.split(os.path.dirname(self.path))[0], 'site')
        fpath = os.path.join(sitePath, subPath)
        if not os.path.exists(os.path.dirname(fpath)):
            os.makedirs(os.path.dirname(fpath))
        f = open(fpath, 'w+')
        return (f, subPath)

    def generateCmdListMarkdown(self, refName, inDict):
        pathInfo = self.makeFilePath(refName, 'Commands')
        f = pathInfo[0]
        subPath = pathInfo[1]
        # for cmdName in inDict:
        for lowerName, cmdName in sorted((k.lower(), k) for k in inDict.keys()):
            mdDict = inDict[cmdName]
            if not mdDict['hidden']:
                self.generateCmdMarkdown(f, refName, cmdName, mdDict)
        f.close()
        return "- '" + refName + "': '" + subPath + "'"

    def generateCmdMarkdown(self, f, refFile, cmdName, inDict):
        f.write('# ' + cmdName + '\n\n')

        baseClass = None
        if inDict['baseClass'] is not None:
            baseClass = inDict['baseClass']
            f.write('<h3>Extends ' + baseClass + '.</h3>\n\n')

        # Command description
        desc = inDict['description']
        desc = desc.replace('\\n', '<BR>')
        if desc == 'MISSING DESCRIPTION':
            print cmdName + ': MISSING DESCRIPTION'
            desc = '<font color="red">' + desc + '</font>'
        f.write(desc + '\n\n')

        # Additional Info: Tag Ex
        if 'tag' in inDict['addedInfo']:
            for tag in inDict['addedInfo']['tag']:
                f.write(tag + '\n\n')

        # File reference
        #fRef = '<font size="2">File Reference: ' + refFile + '</font>'
        #f.write(fRef + '\n\n')

        # Properties
        usesJson = False
        allPropDict = OrderedDict()
        f.write('<h2>- Properties</h2>\n\n')
        # Create an ordered dictionary of properties from the command itself...
        for propName in inDict['properties'].keys():
            allPropDict[propName] = inDict['properties'][propName]

        # Identify the base class...
        if baseClass and baseClass in self.crefDict:
            ref = self.crefDict[baseClass]
            # Add the base class properties if they are not already present...
            for propName in ref['properties']:
                if not propName in allPropDict.keys():
                    allPropDict[propName] = ref['properties'][propName]

        for propName in allPropDict.keys():
            prop = allPropDict[propName]
            f.write('<h3>' + propName + ' (' + prop['category'] + ':' + prop['type'] + ')' + '<br><font size=2>"' + prop['displayName'] +'"</font></h3>\n\n')
            desc = prop['description']
            if desc == 'MISSING DESCRIPTION':
                print cmdName + ': ' + propName + ': MISSING DESCRIPTION'
                desc = '<font color="red">' + desc + '</font>'
            f.write(desc + '\n\n')
            if prop['default'] is not None:
                empty = 'empty' if prop['type'].lower() != 'string' else 'empty string'
                default = prop['default'] if prop['default'] != "" else '<font color=#cc8888>(' + empty + ')</font>'
                f.write('* default: ' + default + '\n\n')
            if prop['enums'] is not None:
                f.write('\t\t' + prop['enums'][0] + '\n')
                if len(prop['enums']) > 1:
                    for enum in prop['enums'][1]:
                        f.write('\t\t    ' + enum[0] + ' = ' + enum[1] + '\n')
                f.write('\n\n')

            if prop['json'] is not None:
                usesJson = True
                f.write('\n\n')
                self.writeStartToggleRegion(f, 'schema.for.' + cmdName + '.' + propName, 'JSON Schema [+]' )
                f.write('<pre><code class="hljs json">')
                jsonTxt = json.dumps(json.loads(prop['json']), indent=2).split('\n')
                for jTxt in jsonTxt:
                    f.write('\t\t' + jTxt + '\n')
                f.write('\n\n')
                f.write('</code></pre>')
                self.writeEndToggleRegion(f)

        # Additional Info: JSON Sample
        if usesJson:
            if 'json' not in inDict['addedInfo']:
                print cmdName + ': MISSING JSON SAMPLE'
                f.write('<font color="red">MISSING JSON SAMPLE</font>\n\n')
            else:
                self.writeStartToggleRegion(f, 'sample.for.' + cmdName + '.' + propName, 'JSON Sample [+]' )
                f.write('<pre><code class="hljs json">')
                for jSamp in inDict['addedInfo']['json']:
                    f.write(jSamp)
                    f.write('\n\n')
                f.write('</code></pre>')
                self.writeEndToggleRegion(f)

        # Used In
        if inDict['meths'] is not None:
            f.write('<h2>- UsedIn</h2>')
            f.write('\n')
            for meth in inDict['meths']:
                    f.write('* ' + meth[0] + '\n\n')
                    #f.write('    <font size=2>' + meth[1] + '</font>' + '\n\n')

        self.generateJavaScripts(f)
        return

    def generateTemplateListMarkdown(self, refName, inDict):
        pathInfo = self.makeFilePath(refName, 'Templates')
        f = pathInfo[0]
        subPath = pathInfo[1]
        self.jsCollapsibleList(f)
        if 'xml' in inDict:
            if 'info' in inDict['xml']:
                f.write('<h3>Notes:</h3>\n\n')
                f.write(str(inDict['xml']['info']) + '\n')
            for tagid in inDict['xml']:
                if tagid == 'info':
                    continue
                tagDict = inDict['xml'][tagid]
                self.generateXmlTemplateMarkdown(f, refName, tagid, tagDict)

            if 'map' in inDict:
                treePathInfo = self.makeMapPath(refName, 'Templates')
                treef = treePathInfo[0]
                print treePathInfo[1]
                treef.write(json.dumps(inDict['map'], indent=2, separators=(',', ': ')))
                treef.close()
        elif 'json' in inDict:
            print refName + ' THIS IS JSON'
        self.generateJavaScripts(f)
        f.close()
        return "- '" + refName + "': '" + subPath + "'"

         # f.write('<h3>' + propName + ' (' + prop['category'] + ':' + prop['type'] + ')' + '<br><font size=2>"' + prop['displayName'] +'"</font></h3>\n\n')
    def generateXmlTemplateMarkdown(self, f, refFile, tagid, inDict):
        if tagid == 'names' or tagid == 'info':
            return
        ps = inDict['parent']
        attrsDict = dict(ps.attrs)

        # CADEN: Might want to use the markdown given id for inline links rather than div id
        f.write('<div id="' + inDict['name'] + '"></div>')

        f.write('\n\n# ' + inDict['name'] + '<br><font size="2">(ClassName:  ' + ps.name + ')</font>')
        if 'info' in inDict.keys():
            f.write('<p>' + inDict['info'] + '</p>')
        self.writeStartToggleRegion(f, inDict['name'], 'Object Property Reference [+]')
        f.write('<table><tr><th>Property</th><th>Value</th></tr>')
        for attrKey in attrsDict.keys():
            f.write('<tr><td>' + attrKey + '</td><td>' + attrsDict[attrKey] + '</td></tr>')
        f.write('</table>')
        self.writeEndToggleRegion(f)

    def writeEndToggleRegion(self, f):
        f.write('</div>')

    def writeStartToggleRegion(self, f, id, caption):
        f.write('<h3><a id="' + id + '.h3link" href="JavaScript:;" onclick="toggle_visibility(' + "'" + id + "'" + ');">' +
                caption + '</a></h3>\n\n<div class="section" style="display:none;" id="' + id + '">')

    def jsCollapsibleList(self, f):
        f.write('''<script type="text/javascript" src="http://code.stephenmorley.org/javascript/collapsible-lists/CollapsibleLists.compressed.js"></script>''')

    def generateJavaScripts(self, f):
        f.write('''
<script type="text/javascript">
<!--
    function toggle_visibility(id) {
       var e = document.getElementById(id);
       var caption = document.getElementById(id + '.h3link');
       var text = caption.innerHTML
       if(e.style.display == 'block')
       {
          e.style.display = 'none';
          caption.innerHTML = text.replace('[-]', '[+]');
       }
       else
       {
          e.style.display = 'block';
          caption.innerHTML = text.replace('[+]', '[-]');
       }
    }
//!-->
</script>''')


def main(argv):
    parseDicts = FileParser().getData()
    try:
        MarkdownProducer(parseDicts, './meth_docs/docs/')
    except Exception as e:
        print 'MarkdownProducer threw an exception: ' + str(e)
        return
    os.chdir('meth_docs')
    os.system('copy mkdocs.yml docs')
    os.system('copy index.md docs')
    os.system('mkdocs build')

if __name__ == '__main__':
    main(sys.argv[1:])
