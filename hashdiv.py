#!/usr/bin/env python3
"""
main.py - Handlers for hashdiv.

Tools:

- Paste text/HTML.  Can be received from JavaScript.
  - If it's HTML, show it in an <iframe> sandbox.
- Code snippet.  With line numbers.  Link to original source.
- Link preview?  OpenGraph, Twitter cards, etc. This is hard and doesn't apply
  to a lot of pages I use.  Probably best to find a service for it.
- get archive.md screenshots?
"""

from flask import Flask, request, render_template, Response, send_from_directory

import glob
import os
import hashlib
import tempfile
import urllib

app = Flask(__name__)

@app.route('/')
def home():
  """Form."""
  app.logger.debug('home')
  return render_template('home.html')


if 0:
  # Don't need this if we set up the application as hashdiv.oils.pub/, rather
  # than oils.pub/hashdiv/
  @app.route('/hashdiv/')
  def test_home():
    """
    uwsgi test.  It doesn't add a URL prefix in the same way that the Apache
    mod_fcgid does.
    """
    app.logger.debug('hashdiv')
    return render_template('home.html')


@app.route('/upload/paste/<path:path>')
def get_paste(path):
  return send_from_directory('upload/paste', path)


@app.route('/pastes')
def list_pastes():
  names = os.listdir('upload/paste')

  show_html = request.args.get('show_html')

  app.logger.debug('%s', names)

  pastes = []
  for name in names:
    rel_path = 'upload/paste/%s' % name
    with open(rel_path) as f:
      data = f.read()

    url = None
    if show_html != '0' and name.endswith('.html'):
      url = rel_path

    pastes.append({'data': data.rstrip(), 'url': url})

  return render_template('pastes.html', pastes=pastes)


@app.route('/delete-pastes', methods=['POST'])
def delete_pastes():
  num_pastes = 0 
  for name in glob.glob('upload/paste/*'):
    app.logger.debug(name)
    num_pastes += 1
    os.unlink(name)

  return 'Deleted %d pastes' % num_pastes


@app.route('/paste', methods=['POST'])
def post_paste():
  """For scraping in JavaScript and posting here

  TODO: Accepting user data is HTML injection; we want a password.

  Or really we only care about a few tags like <a> <span>, etc.
  """
  data = request.form.get('data')
  fmt = request.form.get('format')

  if data is None:
    return Response('Data required'), 400

  raw_data = data.encode('utf-8')  # Must be valid

  app.logger.debug('data %r format %s', data, fmt)
  app.logger.debug('getcwd %s', os.getcwd())

  h = hashlib.md5()
  h.update(raw_data)
  checksum = h.hexdigest()

  is_html = (fmt == 'html' )
  filename = checksum + '.html' if is_html else checksum

  temp_name = 'upload/tmp/%s' % filename
  with open(temp_name, 'wb') as f:
    f.write(raw_data)

  saved_name = 'upload/paste/%s' % filename
  os.rename(temp_name, saved_name)

  return render_template('paste.html', data=data, filename=saved_name, show_iframe=is_html)


@app.route('/link-preview')
def link_preview():
  """Twitter/Facebook-like link preview?  Might want to call out to another service."""
  return 'TODO'


@app.route('/code-snippet')
def code_snippet():
  """Code snippet with line numbers, e.g. like a gist.  Link to Github.

  TODO: Should you require a URL hash here?  To make it immutable?
  """
  url = request.args.get('url')

  start = request.args.get('start')
  end = request.args.get('end')

  try:
    if start:
      start = int(start)
    else:
      start = None

    if end:
      end = int(end)
    else:
      end = None

  except ValueError:
    return Response('Invalid start or end'), 400

  app.logger.debug('snip %s', url)

  # Snip the right lines.

  # TODO: Show HTML line numbers.  And show original URL too.  Github has a
  # hash #L1-L3.

  lines = []
  with urllib.request.urlopen(url) as f:
    for i, line in enumerate(f):
      line_num = i + 1
      if (start is None or start <= line_num) and (end is None or line_num <= end):
        lines.append(line)

  contents = b''.join(lines)

  # TODO: What about rendering text?
  #return render_template('snip.html', contents=contents.decode('utf-8'))
  return Response(contents, mimetype='text/plain')

