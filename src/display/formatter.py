import math

def EMIValueAdjust(value, multi_num=1.0, pow_num=.75):
    return (value * multi_num) ** pow_num

def nodeValueAdjust(value, divide_num=10):
  # second graph: str(float(value) ** .3 / 3)
  return str(math.sqrt(float(value)) / divide_num)

def toScrTitle(id):
  name = 'SCR_'
  for i in range(0, 6 - len(str(id))):
    name += '0'
  return name + str(id)

def toJSNodes(rid, value, name, group, separator=' '):
  if (group == 'nan'): group = 30 # NaN shows same color with 30 (other: gray)
  return "\t{\"name\": \"" + str(toScrTitle(rid)) + separator + str(name) + "\", \"group\": " + str(group) + ", \"value\": " + str(nodeValueAdjust(value)) + "},\n"

def toJSLinks(source, target, value):
  return "\t{\"source\": " + str(source) + ", \"target\": " + str(target) + ", \"value\": " + str(value) + "},\n"


def toTargetIdHtmlFormat(id, url, name, numCoMentionPartners, diversity, mention):
  html = '\t<tr>\n\t\t<td><a class=\"external\" target=\"_blank\"\n\thref=\"https://scicrunch.org/browse/resources/'
  html = html + toScrTitle(id) + '\">' + toScrTitle(id) + '</td>'
  
  len_url = 0 if url is None else len(url)
  if(len_url < 5):
      html = html + '\n\t\t<td> '+ name + '</td>'
  else:
      html = html + '\n\t\t<td><a class=\"external\" target=\"_blank\"\n\thref=\"' + url + '\">' + name + '</a></td>'
  html = html + '\n\t\t<td align="right">' + str(int(numCoMentionPartners)) + '</td>'
  html = html + '\n\t\t<td align="right">' + '{0:.4f}'.format(diversity) + '</td>'
  html = html + '\n\t\t<td align="right">' + str(mention) + '</td>'
  html = html + '\n\t</tr>\n</table>'

  html = html + '<h3>Top 20 co-mention partners: <a class="external" target="_blank" href="help.html"><font color="red">[Help]</font></a></h3>'
  return html

def toMentionIdHtmlFormat(id, url, name, EMI, coMention, mention, mids):
  html = '\t<tr>\n\t\t<td><a class=\"external\" target=\"_blank\"\n\thref=\"https://scicrunch.org/browse/resources/'
  
  html = html + toScrTitle(id) + '\">' + toScrTitle(id) + '</td>'
  len_url = len(url)

  if(len_url < 5):
      html = html + '\n\t\t<td> '+ name + '</td>'
  else:
      html = html + '\n\t\t<td><a class=\"external\" target=\"_blank\"\n\thref=\"' + str(url) + '\">' + str(name) + '</a></td>'
  
  html = html + '\n\t\t<td align="center">' + '<a class=\"external\" target=\"_blank\" href=\"' + str(
      id) + '_main.html\">Go</a>' + '</td>'
  
  html = html + '\n\t\t<td align="right">' + '{0:.4f}'.format(EMI) + '</td>'

  linkPubMed = '<a class="external" target="_blank" href="https://www.ncbi.nlm.nih.gov/pubmed/' + str(','.join([str(s) for s in mids])) + '">' + str(int(coMention)) + '</a>'
  html = html + '\n\t\t<td align="right">' + linkPubMed + '</td>'
  
  html = html + '\n\t\t<td align="right">' + str(mention) + '</td>'
  return html

def toPMIDFormat(rid, mention_id, input_source, confidence, snippet):
  content = '\t<tr height=21 style=\'height:16.0pt\'>\n\t\t<td height=21 align=right style=\'height:16.0pt\'>'
  content += str(toScrTitle(rid))
  content += '\t</td>\n\t\t<td><a class=\"external\" target=\"_blank\"href=\"https://www.ncbi.nlm.nih.gov/pubmed/'
  content += str(mention_id)[5:]
  content += '\">'
  content += str(mention_id)
  content += '</a></td>\n\t\t<td>'
  content += str(input_source)
  content += '</td>\n\t\t<td align=right>'
  content += str(confidence)
  content += '</td>\n\t\t<td colspan=92 style=\'mso-ignore:colspan\'>'

  if str(snippet).strip('\n') == 'NULL':
      content += ' '
  else:
      content += str(snippet)
  content += '</td>\n\t</tr>'
  return content
