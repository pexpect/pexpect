#!/usr/bin/env python
"""Rippy!

This script helps to convert video from one format to another.
This is useful for ripping DVD to mpeg4 video (XviD, DivX).

Features:
    * automatic crop detection
    * mp3 audio compression with resampling options
    * automatic bitrate calculation based on desired target size
    * optional interlace removal, b/w video optimization, video scaling

Run the script with no arguments to start with interactive prompts:
    rippy.py
Run the script with the filename of a config to start automatic mode:
    rippy.py rippy.conf

After Rippy is finished it saves the current configuation in a file called
'rippy.conf' in the local directoy. This can be used to rerun process using the
exact same settings by passing the filename of the conf file as an argument to
Rippy. Rippy will read the options from the file instead of asking you for
options interactively. So if you run rippy with 'dry_run=1' then you can run
the process again later using the 'rippy.conf' file. Don't forget to edit
'rippy.conf' to set 'dry_run=0'!

If you run rippy with 'dry_run' and 'verbose' true then the output generated is
valid command line commands. you could (in theory) cut-and-paste the commands
to a shell prompt. You will need to tweak some values such as crop area and bit
rate because these cannot be calculated in a dry run. This is useful if you
want to get an idea of what Rippy plans to do.

For all the trouble that Rippy goes through to calculate the best bitrate for a
desired target video size it sometimes fails to get it right. Sometimes the
final video size will differ more than you wanted from the desired size, but if
you are really motivated and have a lot of time on your hands then you can run
Rippy again with a manually calculated bitrate. After all compression is done
the first time Rippy will recalculate the bitrate to give you the nearly exact
bitrate that would have worked. You can then edit the 'rippy.conf' file; set
the video_bitrate with this revised bitrate; and then run Rippy all over again.
There is nothing like 4-pass video compression to get it right! Actually, this
could be done in three passes since I don't need to do the second pass
compression before I calculate the revised bitrate. I'm also considering an
enhancement where Rippy would compress ten spread out chunks, 1-minute in
length to estimate the bitrate.

For the latest version see http://rippy.sourceforge.net/

$Id $
Noah Spurrier
"""
import sys, os, re, math, stat, getopt, traceback, types, time
import pexpect

__version__ = '1.2'
__revision__ = '$Revision$'
__all__ = ['main', __version__, __revision__]

GLOBAL_LOGFILE_NAME = "rippy_%d.log" % os.getpid()
GLOBAL_LOGFILE = open (GLOBAL_LOGFILE_NAME, "wb")

###############################################################################
# This giant section defines the prompts and defaults used in interactive mode.
###############################################################################
# Python dictionaries are unordered, so
# I have this list that maintains the order of the keys.
prompts_key_order = (
'verbose_flag',
'dry_run_flag',
'video_source_filename',
'video_final_filename',
'video_length',
'video_aspect_ratio',
'video_scale',
'video_encode_passes',
'video_codec',
'video_fourcc_override',
'video_target_size',
'video_bitrate',
'video_bitrate_overhead',
'video_crop_area',
'video_deinterlace_flag',
'video_gray_flag',
'subtitle_id',
'audio_id',
'audio_codec',
'audio_raw_filename',
'audio_sample_rate',
'audio_bitrate',
'audio_lowpass_filter',
'delete_tmp_files_flag'
)
#
# The 'prompts' dictionary holds all the messages shown to the user in
# interactive mode. The 'prompts' dictionary schema is defined as follows:
#    prompt_key : ( default value, prompt string, help string, level of difficulty (0,1,2) )
#
prompts = {
'video_source_filename':("dvd://1", 'video source filename?', """This is the filename of the video that you want to convert from.
It can be any file that mencoder supports.
You can also choose a DVD device using the dvd://1 syntax.
Title 1 is usually the main title on a DVD.""",0),
#'video_transcoded_filename':("videodump.avi", 'Video transcoded filename?', """This is the temporary file where the video will be stored in the new format.""",2),
'video_final_filename':("video_final.avi", "video final filename?", """This is the name of the final video.""",0),
'audio_raw_filename':("audiodump.wav", "audio raw filename?", """This is the audio raw PCM filename. This is prior to compression.
Note that mplayer automatically names this audiodump.wav, so
currently changing this does not work.""",2),
#'audio_compressed_filename':("audiodump.mp3","Audio compressed filename?", """This is the name of the compressed audio that will be mixed
#into the final video. Normally you don't need to change this.""",2),
'video_length':("calc","video length in seconds?","""This sets the length of the video in seconds. Set to 'calc' to calculate the length from the
raw audio stream. That's a hack because mplayer cannot get the length of
the video from the source video file. Normally you don't need to change this.""",1),
'video_aspect_ratio':("calc","aspect ratio?","""This sets the aspect ratio of the video. Most DVDs are 16/9 or 4/3.""",1),
'video_scale':("none","video scale?","""This scales the video to the given output size. The default is to do no scaling.
You may type in a resolution such as 320x240 or you may use presets.
    qntsc: 352x240 (NTSC quarter screen)
    qpal:  352x288 (PAL quarter screen)
    ntsc:  720x480 (standard NTSC)
    pal:   720x576 (standard PAL)
    sntsc: 640x480 (square pixel NTSC)
    spal:  768x576 (square pixel PAL)""",1),
'video_codec':("mpeg4","video codec?","""This is the video compression to use. This is passed directly to mencoder, so
any format that it recognizes will work. DivX and XviD use mpeg4.
Some common codecs include:
mjpeg, h263, h263p, h264, mpeg4, msmpeg4, wmv1, wmv2, mpeg1video, mpeg2video, huffyuv, ffv1.
See mencoder manual for details.""",2),
'audio_codec':("mp3","audio codec?","""This is the audio compression to use. This is passed directly to mencoder, so
any format that it recognizes will work.
Some common codecs include:
mp3, mp2, aac, pcm
See mencoder manual for details.""",2),
'video_fourcc_override':("XVID","force fourcc code?","""This forces the fourcc codec to the given value. XVID is safest for Windows.
The following are common fourcc values:
    FMP4 - This is the mencoder default. This is the "real" value.
    XVID - used by Xvid (safest)
    DX50 -
    MP4S - Microsoft""",2),
'video_encode_passes':("2","number of encode passes?","""This sets how many passes to use to encode the video. You can choose 1 or 2.
Using two pases takes twice as long as one pass, but produces a better
quality video. I found that the effect is not that noticable.""",1),
'verbose_flag':("Y","verbose output?","""This sets verbose output. If true then all commands and arguments are printed
before they are run. This is useful to see exactly how commands are run.""",1),
'dry_run_flag':("N","dry run?","""This sets 'dry run' mode. If true then commands are not run. This is useful
if you want to see what would happen by running the script.""",1),
'video_bitrate':("calc","video bitrate?","""This sets the video bitrate. This overrides video_target_size.
Set to 'calc' to automatically estimate the bitrate based on the
video final target size.""",1),
'video_target_size':("700","video final target size in MB?","""This sets the target video size that you want to end up with.
This is over-ridden by video_bitrate. In other words, if you specify
video_bitrate then video_target_size is ignored.
Due to the unpredictable nature of compression the final video size may not
exactly match. The following are common CDR sizes:
    180MB CDR (21 minutes) holds 193536000 bytes
    550MB CDR (63 minutes) holds 580608000 bytes
    650MB CDR (74 minutes) holds 681984000 bytes
    700MB CDR (80 minutes) holds 737280000 bytes""",0),
'video_bitrate_overhead':("1.19","bitrate overhead factor?","""I found that a 19% overhead (1.19 factor) produces
a bitrate estimate that results in video files that are just under the
target size. For a 700MB CDR, there will be about 4% free. Adjust this value if
you want to leave more room for other files such as subtitle files.
If you specify video_bitrate then this value is ignored.""",2),
'video_crop_area':("detect","crop area?","""This sets the crop area to remove black bars from the top or sides of the video.
This helps save space. Set to 'detect' to automatically detect the crop area.
Set to 'none' to not crop the video. Normally you don't need to change this.""",1),
'video_deinterlace_flag':("N","is the video interlaced?","""This sets the deinterlace flag. If set then mencoder will be instructed
to filter out interlace artifacts.""",1),
'video_gray_flag':("N","is the video black and white (gray)?","""This improves output for black and white video.""",1),
'subtitle_id':("0","Subtitle ID stream?","""This selects the subtitle stream to extract from the source video.
Normally, 0 is the English subtitle stream for a DVD.
Subtitles IDs with higher numbers may be other languages.""",1),
'audio_id':("128","audio ID stream?","""This selects the audio stream to extract from the source video.
If your source is a VOB file (DVD) then stream IDs start at 128.
Normally, 128 is the main audio track for a DVD.
Tracks with higher numbers may be other language dubs or audio commentary.""",1),
'audio_sample_rate':("32000","audio sample rate (Hz) 48000, 44100, 32000, 24000, 12000","""This sets the rate at which the compressed audio will be resampled.
DVD audio is 48 kHz whereas music CDs use 44.1 kHz. The higher the sample rate
the more space the audio track will take. That will leave less space for video.
32 kHz is a good trade-off if you are trying to fit a video onto a CD.""",1),
'audio_bitrate':("96","audio bitrate (kbit/s) 192, 128, 96, 64?","""This sets the bitrate for MP3 audio compression.
The higher the bitrate the more space the audio track will take.
That will leave less space for video. Most people find music to be acceptable
at 128 kBitS. 96 kBitS is a good trade-off if you are trying to fit a video onto a CD.""",1),
'audio_lowpass_filter':("16","audio lowpass filter (kHz)?","""This sets the low-pass filter for the audio.
Normally this should be half of the audio sample rate.
This improves audio compression and quality.
Normally you don't need to change this.""",1),
'delete_tmp_files_flag':("N","delete temporary files when finished?","""If Y then %s, audio_raw_filename, and 'divx2pass.log' will be deleted at the end."""%GLOBAL_LOGFILE_NAME,1)
}

##############################################################################
# This is the important convert control function
##############################################################################
def convert (options):
    """This is the heart of it all -- this performs an end-to-end conversion of
    a video from one format to another. It requires a dictionary of options.
    The conversion process will also add some keys to the dictionary
    such as length of the video and crop area. The dictionary is returned.
    This options dictionary could be used again to repeat the convert process
    (it is also saved to rippy.conf as text).
    """
    try:
        sid = int(options['subtitle_id'])
        print "# extract subtitles"
        apply_smart (extract_subtitles, options)
    except:
        print "# do not extract subtitles."

    # Optimization alert!
    # I really only need to calculate the exact video length if the user
    # selected 'calc' for video_bitrate or
    # selected 'detect' for video_crop_area.
    if options['video_bitrate']=='calc' or options['video_crop_area']=='detect':
        # As strange as it seems, the only reliable way to calculate the length
        # of a video (in seconds) is to extract the raw, uncompressed PCM audio stream
        # and then calculate the length of that. This is because MP4 video is VBR, so
        # you cannot get exact time based on compressed size.
        if options['video_length']=='calc':
            print "# extract PCM raw audio to %s" % (options['audio_raw_filename'])
            apply_smart (extract_audio, options)
            options['video_length'] = apply_smart (get_length, options)
            print "# Length of raw audio file : %d seconds (%0.2f minutes)" % (options['video_length'], float(options['video_length'])/60.0)

    if options['video_bitrate']=='calc':
        options['video_bitrate'] = options['video_bitrate_overhead'] * apply_smart (calc_video_bitrate, options) 
    print "# video bitrate : " + str(options['video_bitrate'])

    if options['video_crop_area']=='detect':
        options['video_crop_area'] = apply_smart (crop_detect, options)
    print "# crop area : " + str(options['video_crop_area'])

    print "# compress video"
    apply_smart (compress_video, options)

    print "# delete temporary files:",
    if options['delete_tmp_files_flag']:
        print "yes"
        apply_smart (delete_tmp_files, options)
    else:
        print "no"

    video_actual_size = get_filesize (options['video_final_filename'])
    revised_bitrate = calculate_revised_bitrate (options['video_bitrate'], options['video_target_size'], video_actual_size)

    o = ["# options used to create video\n"]
    o.append("# revised video_bitrate : %d\n" % revised_bitrate)
    for k,v in options.iteritems():
        o.append (" %30s : %s\n" % (k, v))
    print '# '.join(o)
    fout = open("rippy.conf","wb").write(''.join(o))
    
    print "# final actual video size = %d" % video_actual_size
    if video_actual_size > options['video_target_size']:
        print "# FINAL VIDEO SIZE IS GREATER THAN DESIRED TARGET"
        print "# final video size is %d bytes over target size" % (video_actual_size - options['video_target_size'])
    else:
        print "# final video size is %d bytes under target size" % (options['video_target_size'] - video_actual_size)
    print "# If you want to run the entire compression process all over again"
    print "# to get closer to the target video size then trying using a revised"
    print "# video_bitrate of %d" % revised_bitrate

    return options

##############################################################################

def exit_with_usage(exit_code=1):
    print globals()['__doc__']
    print 'version:', globals()['__version__']
    print 'revision:', globals()['__revision__']
    os._exit(exit_code)

def check_missing_requirements ():
    """This list of missing requirements (mencoder, mplayer, lame, and mkvmerge).
    Returns None if all requirements are in the execution path.
    """
    missing = []
    if pexpect.which("mencoder") is None:
        missing.append("mencoder")
    if pexpect.which("mplayer") is None:
        missing.append("mplayer")
    #if pexpect.which("lame") is None:
    #    missing.append("lame")
    #if pexpect.which("mkvmerge") is None:
    #    missing.append("mkvmerge")
    if len(missing)==0:
        return None
    return missing

def input_option (message, default_value="", help=None, level=0, max_level=0):
    """This is a fancy raw_input function.
    If the user enters '?' then the contents of help is printed.
    
    The 'level' and 'max_level' are used to adjust which advanced options
    are printed. 'max_level' is the level of options that the user wants
    to see. 'level' is the level of difficulty for this particular option.
    If this level is <= the max_level the user wants then the
    message is printed and user input is allowed; otherwise, the
    default value is returned automatically without user input.
    """
    if default_value != '':
        message = "%s [%s] " % (message, default_value)
    if level > max_level:
        return default_value
    while 1:
        user_input = raw_input (message)
        if user_input=='?':
            print help
        elif user_input=='':
            return default_value
        else:
            break
    return user_input

def progress_callback (d=None):
    """This callback simply prints a dot to show activity.
    This is used when running external commands with pexpect.run.
    """
    sys.stdout.write (".")
    sys.stdout.flush()

def run(cmd):
    global GLOBAL_LOGFILE
    print >>GLOBAL_LOGFILE, cmd
    (command_output, exitstatus) = pexpect.run(cmd, events={pexpect.TIMEOUT:progress_callback}, timeout=5, withexitstatus=True, logfile=GLOBAL_LOGFILE)
    if exitstatus != 0:
        print "RUN FAILED. RETURNED EXIT STATUS:", exitstatus
        print >>GLOBAL_LOGFILE, "RUN FAILED. RETURNED EXIT STATUS:", exitstatus
    return (command_output, exitstatus)

def apply_smart (func, args):
    """This is similar to func(**args), but this won't complain about 
    extra keys in 'args'. This ignores keys in 'args' that are 
    not required by 'func'. This passes None to arguments that are
    not defined in 'args'. That's fine for arguments with a default valeue, but
    that's a bug for required arguments. I should probably raise a TypeError.
    The func parameter can be a function reference or a string.
    If it is a string then it is converted to a function reference.
    """
    if type(func) is type(''):
        if func in globals():
            func = globals()[func]
        else:
            raise NameError("name '%s' is not defined" % func)
    if hasattr(func,'im_func'): # Handle case when func is a class method.
        func = func.im_func
    argcount = func.func_code.co_argcount
    required_args = dict([(k,args.get(k)) for k in func.func_code.co_varnames[:argcount]])
    return func(**required_args)

def count_unique (items):
    """This takes a list and returns a sorted list of tuples with a count of each unique item in the list.
    Example 1:
        count_unique(['a','b','c','a','c','c','a','c','c'])
    returns:
        [(5,'c'), (3,'a'), (1,'b')]
    Example 2 -- get the most frequent item in a list:
        count_unique(['a','b','c','a','c','c','a','c','c'])[0][1]
    returns:
        'c'
    """
    stats = {}
    for i in items:
        if i in stats:
            stats[i] = stats[i] + 1
        else:
            stats[i] = 1
    stats = [(v, k) for k, v in stats.items()]
    stats.sort()
    stats.reverse()
    return stats

def calculate_revised_bitrate (video_bitrate, video_target_size, video_actual_size):
    """This calculates a revised video bitrate given the video_bitrate used,
    the actual size that resulted, and the video_target_size.
    This can be used if you want to compress the video all over again in an
    attempt to get closer to the video_target_size.
    """
    return int(math.floor(video_bitrate * (float(video_target_size) / float(video_actual_size))))

def get_aspect_ratio (video_source_filename):
    """This returns the aspect ratio of the original video.
    This is usualy 1.78:1(16/9) or 1.33:1(4/3).
    This function is very lenient. It basically guesses 16/9 whenever
    it cannot figure out the aspect ratio.
    """
    cmd = "mplayer %s -vo png -ao null -frames 1" % video_source_filename
    (command_output, exitstatus) = run(cmd)
    ar = re.findall("Movie-Aspect is ([0-9]+\.?[0-9]*:[0-9]+\.?[0-9]*)", command_output)
    if len(ar)==0:
        return '16/9'
    if ar[0] == '1.78:1':
        return '16/9'
    if ar[0] == '1.33:1':
        return '4/3'
    return '16/9'
    #idh = re.findall("ID_VIDEO_HEIGHT=([0-9]+)", command_output)
    #if len(idw)==0 or len(idh)==0:
    #    print 'WARNING!'
    #    print 'Could not get aspect ration. Assuming 1.78:1 (16/9).'
    #    return 1.78
    #return float(idw[0])/float(idh[0])
#ID_VIDEO_WIDTH=720
#ID_VIDEO_HEIGHT=480
#Movie-Aspect is 1.78:1 - prescaling to correct movie aspect.


def get_aid_list (video_source_filename):
    """This returns a list of audio ids in the source video file.
    TODO: Also extract ID_AID_nnn_LANG to associate language. Not all DVDs include this.
    """
    cmd = "mplayer %s -vo null -ao null -frames 0 -identify" % video_source_filename
    (command_output, exitstatus) = run(cmd)
    idl = re.findall("ID_AUDIO_ID=([0-9]+)", command_output)
    idl.sort()
    return idl

def get_sid_list (video_source_filename):
    """This returns a list of subtitle ids in the source video file.
    TODO: Also extract ID_SID_nnn_LANG to associate language. Not all DVDs include this.
    """
    cmd = "mplayer %s -vo null -ao null -frames 0 -identify" % video_source_filename
    (command_output, exitstatus) = run(cmd)
    idl = re.findall("ID_SUBTITLE_ID=([0-9]+)", command_output)
    idl.sort()
    return idl
    
def extract_audio (video_source_filename, audio_id=128, verbose_flag=0, dry_run_flag=0):
    """This extracts the given audio_id track as raw uncompressed PCM from the given source video.
        Note that mplayer always saves this to audiodump.wav.
        At this time there is no way to set the output audio name.
    """
    #cmd = "mplayer %(video_source_filename)s -vc null -vo null -aid %(audio_id)s -ao pcm:fast -noframedrop" % locals()
    cmd = "mplayer %(video_source_filename)s -vc dummy -vo null -aid %(audio_id)s -ao pcm:fast -noframedrop" % locals()
    if verbose_flag: print cmd
    if not dry_run_flag:
        run(cmd)
        print

def extract_subtitles (video_source_filename, subtitle_id=0, verbose_flag=0, dry_run_flag=0):
    """This extracts the given subtitle_id track as VOBSUB format from the given source video.
    """
    cmd = "mencoder %(video_source_filename)s -o /dev/null -nosound -ovc copy -vobsubout subtitles -vobsuboutindex 0 -sid %(subtitle_id)s" % locals()
    if verbose_flag: print cmd
    if not dry_run_flag:
        run(cmd)
        print

def get_length (audio_raw_filename):
    """This attempts to get the length of the media file (length is time in seconds).
    This should not be confused with size (in bytes) of the file data.
    This is best used on a raw PCM AUDIO file because mplayer cannot get an accurate
    time for many compressed video and audio formats -- notably MPEG4 and MP3.
    Weird...
    This returns -1 if it cannot get the length of the given file.
    """
    cmd = "mplayer %s -vo null -ao null -frames 0 -identify" % audio_raw_filename
    (command_output, exitstatus) = run(cmd)
    idl = re.findall("ID_LENGTH=([0-9.]*)", command_output)
    idl.sort()
    if len(idl) != 1:
        print "ERROR: cannot get length of raw audio file."
        print "command_output of mplayer identify:"
        print command_output
        print "parsed command_output:"
        print str(idl)
        return -1
    return float(idl[0])

def get_filesize (filename):
    """This returns the number of bytes a file takes on storage."""
    return os.stat(filename)[stat.ST_SIZE]

def calc_video_bitrate (video_target_size, audio_bitrate, video_length, extra_space=0, dry_run_flag=0):
    """This gives an estimate of the video bitrate necessary to
    fit the final target size.  This will take into account room to
    fit the audio and extra space if given (for container overhead or whatnot).
        video_target_size is in bytes,
        audio_bitrate is bits per second (96, 128, 256, etc.) ASSUMING CBR,
        video_length is in seconds,
        extra_space is in bytes.
    a 180MB CDR (21 minutes) holds 193536000 bytes.
    a 550MB CDR (63 minutes) holds 580608000 bytes.
    a 650MB CDR (74 minutes) holds 681984000 bytes.
    a 700MB CDR (80 minutes) holds 737280000 bytes.
    """
    if dry_run_flag:
        return -1
    if extra_space is None: extra_space = 0
    #audio_size = os.stat(audio_compressed_filename)[stat.ST_SIZE]
    audio_size = (audio_bitrate * video_length * 1000) / 8.0
    video_target_size = video_target_size - audio_size - extra_space
    return (int)(calc_video_kbitrate (video_target_size, video_length))

def calc_video_kbitrate (target_size, length_secs):
    """Given a target byte size free for video data, this returns the bitrate in kBit/S.
    For mencoder vbitrate 1 kBit = 1000 Bits -- not 1024 bits.
        target_size = bitrate * 1000 * length_secs / 8
        target_size = bitrate * 125 * length_secs
        bitrate     = target_size/(125*length_secs)
    """
    return int(target_size / (125.0 * length_secs))

def crop_detect (video_source_filename, video_length, dry_run_flag=0):
    """This attempts to figure out the best crop for the given video file.
    Basically it runs crop detect for 5 seconds on three different places in the video.
    It picks the crop area that was most often detected.
    """
    skip = int(video_length/9)
    sample_length = 5
    cmd1 = "mencoder %s -quiet -ss %d -endpos %d -o /dev/null -nosound -ovc lavc -vf cropdetect" % (video_source_filename,   skip, sample_length)
    cmd2 = "mencoder %s -quiet -ss %d -endpos %d -o /dev/null -nosound -ovc lavc -vf cropdetect" % (video_source_filename, 2*skip, sample_length)
    cmd3 = "mencoder %s -quiet -ss %d -endpos %d -o /dev/null -nosound -ovc lavc -vf cropdetect" % (video_source_filename, 3*skip, sample_length)
    if dry_run_flag:
        return "0:0:0:0"
    (command_output1, exitstatus1) = run(cmd1)
    (command_output2, exitstatus2) = run(cmd2)
    (command_output3, exitstatus3) = run(cmd3)
    idl = re.findall("-vf crop=([0-9]+:[0-9]+:[0-9]+:[0-9]+)", command_output1)
    idl = idl + re.findall("-vf crop=([0-9]+:[0-9]+:[0-9]+:[0-9]+)", command_output2)
    idl = idl + re.findall("-vf crop=([0-9]+:[0-9]+:[0-9]+:[0-9]+)", command_output3)
    items_count = count_unique(idl)
    return items_count[0][1]

def compress_video (video_source_filename, video_final_filename, audio_id=128, video_bitrate=1000, video_codec='mpeg4', audio_codec='mp3', video_fourcc_override='FMP4', video_gray_flag=0, video_crop_area=None, video_aspect_ratio='16/9', video_scale=None, video_encode_passes=2, video_deinterlace_flag=0, audio_lowpass_filter=None, audio_sample_rate=None, audio_bitrate=None, verbose_flag=0, dry_run_flag=0):
    """This compresses the video and audio of the given source video filename to the transcoded filename.
        This does a two-pass compression (I'm assuming mpeg4, I should probably make this smarter for other formats).
    audio_lowpass_filter is DISABLED
For VCD and SVCD use acodec mp2:
mencoder movie.wmv -o movie.avi -ovc lavc -oac lavc -lavcopts acodec=mp2:abitrate=224
    """
    #
    # build video filter (-vf) argument 
    #
    video_filter = ''
    if video_crop_area and video_crop_area.lower()!='none':
        video_filter = video_filter + 'crop=%s' % video_crop_area
    if video_deinterlace_flag:
        if video_filter != '':
            video_filter = video_filter + ','
        video_filter = video_filter + 'pp=md'
    if video_scale and video_scale.lower()!='none':
        if video_filter != '':
            video_filter = video_filter + ','
        video_filter = video_filter + 'scale=%s' % video_scale
    # optional video rotation -- were you holding your camera sideways?
    #if video_filter != '':
    #    video_filter = video_filter + ','
    #video_filter = video_filter + 'rotate=2' 
    if video_filter != '':
        video_filter = '-vf ' + video_filter

    #
    # build audio_filter argument
    #
    audio_filter = ''
    if audio_sample_rate:
        if audio_filter != '':
            audio_filter = audio_filter + ','
        audio_filter = audio_filter + 'lavcresample=%s' % audio_sample_rate 
    if audio_filter != '':
        audio_filter = '-af ' + audio_filter
    if audio_sample_rate:
        audio_filter = '-srate %d ' % audio_sample_rate + audio_filter

    #
    # build lavcopts argument
    #
    #lavcopts = '-lavcopts vcodec=%s:vbitrate=%d:mbd=2:aspect=%s:acodec=%s:abitrate=%d:vpass=1' % (video_codec,video_bitrate,audio_codec,audio_bitrate)
    lavcopts = '-lavcopts vcodec=%(video_codec)s:vbitrate=%(video_bitrate)d:mbd=2:aspect=%(video_aspect_ratio)s:acodec=%(audio_codec)s:abitrate=%(audio_bitrate)d:vpass=1' % (locals())
    if video_gray_flag:
        lavcopts = lavcopts + ':gray'

#    #
#    # build lameopts argument
#    #
#    lameopts = ''
#    if audio_bitrate:
#        if lameopts != '':
#            lameopts = lameopts + ':'
#        lameopts = lameopts + 'cbr:br=%s' % audio_bitrate
#    if audio_lowpass_filter:
#        if lameopts != '':
#            lameopts = lameopts + ':'
#        lameopts = lameopts + 'lowpassfreq=%s' % audio_lowpass_filter
#    if lameopts != '':
#        lameopts = '-lameopts ' + lameopts
#    #/usr/bin/mencoder VIDEO.vob -o video.avi -aid 128 -ffourcc XVID -oac mp3lame -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=922:mbd=2:vpass=2 -vf crop=704:368:8:54 -lameopts cbr:br=96 -af resample=32000 
#    audio_copy_codec_options = lameopts
#
    #
    # do the first pass video compression
    #
    cmd = "mencoder %(video_source_filename)s -aid %(audio_id)s -o %(video_final_filename)s -ffourcc %(video_fourcc_override)s -ovc lavc -oac lavc %(lavcopts)s %(video_filter)s %(audio_filter)s" % locals()
    if verbose_flag: print cmd
    if not dry_run_flag:
        run(cmd)
        print

    # If not doing two passes then return early.
    if video_encode_passes!='2':
        return

    #
    # do the second pass video compression
    #
    cmd = cmd.replace ('vpass=1', 'vpass=2')
    if verbose_flag: print cmd
    if not dry_run_flag:
        run(cmd)
        print
    return

def compress_audio (audio_raw_filename, audio_compressed_filename, audio_lowpass_filter=None, audio_sample_rate=None, audio_bitrate=None, verbose_flag=0, dry_run_flag=0):
    """This is depricated.
    This compresses the raw audio file to the compressed audio filename.
    """
    cmd = 'lame -h --athaa-sensitivity 1' # --cwlimit 11"
    if audio_lowpass_filter:
        cmd = cmd + ' --lowpass ' + audio_lowpass_filter
    if audio_bitrate:
        #cmd = cmd + ' --abr ' + audio_bitrate
        cmd = cmd + ' --cbr -b ' + audio_bitrate
    if audio_sample_rate:
        cmd = cmd + ' --resample ' + audio_sample_rate
    cmd = cmd + ' ' + audio_raw_filename + ' ' + audio_compressed_filename
    if verbose_flag: print cmd
    if not dry_run_flag:
        (command_output, exitstatus) = run(cmd)
        print
        if exitstatus != 0:
            raise Exception('ERROR: lame failed to compress raw audio file.')

def mux (video_final_filename, video_transcoded_filename, audio_compressed_filename, video_container_format, verbose_flag=0, dry_run_flag=0):
    """This is depricated. I used to use a three-pass encoding where I would mix the audio track separately, but
    this never worked very well (loss of audio sync)."""
    if video_container_format.lower() == 'mkv': # Matroska
        mux_mkv (video_final_filename, video_transcoded_filename, audio_compressed_filename, verbose_flag, dry_run_flag)
    if video_container_format.lower() == 'avi':
        mux_avi (video_final_filename, video_transcoded_filename, audio_compressed_filename, verbose_flag, dry_run_flag)

def mux_mkv (video_final_filename, video_transcoded_filename, audio_compressed_filename, verbose_flag=0, dry_run_flag=0):
    """This is depricated."""
    cmd = 'mkvmerge -o %s --noaudio %s %s' % (video_final_filename, video_transcoded_filename, audio_compressed_filename)
    if verbose_flag: print cmd
    if not dry_run_flag:
        run(cmd)
        print

def mux_avi (video_final_filename, video_transcoded_filename, audio_compressed_filename, verbose_flag=0, dry_run_flag=0):
    """This is depricated."""
    cmd = 'mencoder -oac copy -ovc copy -o %s -audiofile %s %s' % (video_final_filename, audio_compressed_filename, video_transcoded_filename)
    if verbose_flag: print cmd
    if not dry_run_flag:
        run(cmd)
        print

def delete_tmp_files (audio_raw_filename, verbose_flag=0, dry_run_flag=0):
    global GLOBAL_LOGFILE_NAME
    file_list = ' '.join([GLOBAL_LOGFILE_NAME, 'divx2pass.log', audio_raw_filename ])
    cmd = 'rm -f ' + file_list
    if verbose_flag: print cmd
    if not dry_run_flag:
        run(cmd)
        print
    
##############################################################################
# This is the interactive Q&A that is used if a conf file was not given.
##############################################################################
def interactive_convert ():
    global prompts, prompts_key_order

    print globals()['__doc__']
    print
    print "=============================================="
    print " Enter '?' at any question to get extra help."
    print "=============================================="
    print
  
    # Ask for the level of options the user wants. 
    # A lot of code just to print a string!
    level_sort = {0:'', 1:'', 2:''} 
    for k in prompts:
        level = prompts[k][3]
        if level < 0 or level > 2:
            continue
        level_sort[level] += "    " + prompts[k][1] + "\n"
    level_sort_string = "This sets the level for advanced options prompts. Set 0 for simple, 1 for advanced, or 2 for expert.\n"
    level_sort_string += "[0] Basic options:\n" + str(level_sort[0]) + "\n"
    level_sort_string += "[1] Advanced options:\n" + str(level_sort[1]) + "\n"
    level_sort_string += "[2] Expert options:\n" + str(level_sort[2])
    c = input_option("Prompt level (0, 1, or 2)?", "0", level_sort_string)
    max_prompt_level = int(c)

    options = {}
    for k in prompts_key_order:
        if k == 'video_aspect_ratio':
            guess_aspect = get_aspect_ratio(options['video_source_filename'])
            options[k] = input_option (prompts[k][1], guess_aspect, prompts[k][2], prompts[k][3], max_prompt_level)
        elif k == 'audio_id':
            aid_list = get_aid_list (options['video_source_filename'])
            default_id = '128'
            if max_prompt_level>=prompts[k][3]: 
                if len(aid_list) > 1:
                    print "This video has more than one audio stream. The following stream audio IDs were found:"
                    for aid in aid_list:
                        print "    " + aid
                    default_id = aid_list[0]
                else:
                    print "WARNING!"
                    print "Rippy was unable to get the list of audio streams from this video."
                    print "If reading directly from a DVD then the DVD device might be busy."
                    print "Using a default setting of stream id 128 (main audio on most DVDs)."
                    default_id = '128'
            options[k] = input_option (prompts[k][1], default_id, prompts[k][2], prompts[k][3], max_prompt_level)
        elif k == 'subtitle_id':
            sid_list = get_sid_list (options['video_source_filename'])
            default_id = 'None'
            if max_prompt_level>=prompts[k][3]:
                if len(sid_list) > 1:
                    print "This video has more than one subtitle stream. The following stream subtitle IDs were found:"
                    for sid in sid_list:
                        print "    " + sid
                    default_id = sid_list[0]
                else:
                    print "WARNING!"
                    print "Unable to get the list of subtitle streams from this video. It may have none."
                    print "Setting default to None."
                    default_id = 'None'
            options[k] = input_option (prompts[k][1], default_id, prompts[k][2], prompts[k][3], max_prompt_level)
        elif k == 'audio_lowpass_filter':
            lowpass_default =  "%.1f" % (math.floor(float(options['audio_sample_rate']) / 2.0))
            options[k] = input_option (prompts[k][1], lowpass_default, prompts[k][2], prompts[k][3], max_prompt_level)
        else:
            # Don't bother asking for video_target_size or video_bitrate_overhead if bitrate was set
            if (k=='video_target_size' or k=='video_bitrate_overhead') and options['video_bitrate']!='calc':
                continue
            options[k] = input_option (prompts[k][1], prompts[k][0], prompts[k][2], prompts[k][3], max_prompt_level)

    #options['video_final_filename'] = options['video_final_filename'] + "." + options['video_container_format']

    print "=========================================================================="
    print "Ready to Rippy!"
    print
    print "The following options will be used:"
    for k,v in options.iteritems():
        print "%27s : %s" % (k, v)

    print
    c = input_option("Continue?", "Y")
    c = c.strip().lower()
    if c[0] != 'y':
        print "Exiting..."
        os._exit(1)
    return options

def clean_options (d):
    """This validates and cleans up the options dictionary.
    After reading options interactively or from a conf file
    we need to make sure that the values make sense and are
    converted to the correct type.
    1. Any key with "_flag" in it becomes a boolean True or False.
    2. Values are normalized ("No", "None", "none" all become "none";
    "Calcluate", "c", "CALC" all become "calc").
    3. Certain values are converted from string to int.
    4. Certain combinations of options are invalid or override each other.
    This is a rather annoying function, but then so it most cleanup work.
    """
    for k in d:
        d[k] = d[k].strip()
        # convert all flag options to 0 or 1
        if '_flag' in k:
            if type(d[k]) is types.StringType:
                if d[k].strip().lower()[0] in 'yt1': #Yes, True, 1
                    d[k] = 1
                else:
                    d[k] = 0
    d['video_bitrate'] = d['video_bitrate'].lower()
    if d['video_bitrate'][0]=='c':
        d['video_bitrate']='calc'
    else:
        d['video_bitrate'] = int(float(d['video_bitrate']))
    try:
        d['video_target_size'] = int(d['video_target_size']) 
        if d['video_target_size'] == 180:
            d['video_target_size'] = 193536000
        elif d['video_target_size'] == 550:
            d['video_target_size'] = 580608000
        elif d['video_target_size'] == 650:
            d['video_target_size'] = 681984000
        elif d['video_target_size'] == 700:
            d['video_target_size'] = 737280000
        else:
            d['video_target_size'] = d['video_target_size'] * (1024 * 1024)
    except:
        d['video_target_size'] = 'none'
 
    try:
        d['video_bitrate_overhead'] = float(d['video_bitrate_overhead'])
    except:
        d['video_bitrate_overhead'] = -1.0

    d['audio_bitrate'] = int(d['audio_bitrate'])
    d['audio_sample_rate'] = int(d['audio_sample_rate'])

#    assert (d['video_bitrate']=='calc' and d['video_target_size']!='none')
# or (d['video_bitrate']!='calc' and d['video_target_size']=='none')

    d['video_scale'] = d['video_scale'].lower()
    if d['video_scale'][0]=='n':
        d['video_scale']='none'
    else:
        al = re.findall("([0-9]+).*?([0-9]+)", d['video_scale'])
        d['video_scale']=al[0][0]+':'+al[0][1]
    d['video_crop_area'] = d['video_crop_area'].lower()
    if d['video_crop_area'][0]=='n':
        d['video_crop_area']='none'
    d['video_length'] = d['video_length'].lower()
    if d['video_length'][0]=='c':
        d['video_length']='calc'
    return d

def main ():
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h?', ['help','h','?'])
    except Exception, e:
        print str(e)
        exit_with_usage()
    command_line_options = dict(optlist)
    # There are a million ways to cry for help. These are but a few of them.
    if [elem for elem in command_line_options if elem in ['-h','--h','-?','--?','--help']]:
        exit_with_usage(0)

    missing = check_missing_requirements()
    if missing is not None:
        print
        print "=========================================================================="
        print "ERROR!"
        print "Some required external commands are missing."
        print "please install the following packages:"
        print str(missing)
        print "=========================================================================="
        print
        c = input_option("Continue?", "Y")
        c = c.strip().lower()
        if c[0] != 'y':
            print "Exiting..."
            os._exit(1)

    if len(args) > 0:
        # cute one-line string to dictionary parse (two-lines if you count this comment):
        options = dict(re.findall('([^: \t\n]*)\s*:\s*(".*"|[^ \t\n]*)', file(args[0]).read()))
        options = clean_options(options)
        convert (options)
    else:
        options = interactive_convert ()
        options = clean_options(options)
        convert (options)
    print "# Done!"
    
if __name__ == "__main__":
    try:
        start_time = time.time()
        print time.asctime()
        main()
        print time.asctime()
        print "TOTAL TIME IN MINUTES:",
        print (time.time() - start_time) / 60.0
    except Exception, e:
        tb_dump = traceback.format_exc()
        print "=========================================================================="
        print "ERROR -- Unexpected exception in script."
        print str(e)
        print str(tb_dump)
        print "=========================================================================="
        print >>GLOBAL_LOGFILE, "=========================================================================="
        print >>GLOBAL_LOGFILE, "ERROR -- Unexpected exception in script."
        print >>GLOBAL_LOGFILE, str(e)
        print >>GLOBAL_LOGFILE, str(tb_dump)
        print >>GLOBAL_LOGFILE, "=========================================================================="
        exit_with_usage(3)

