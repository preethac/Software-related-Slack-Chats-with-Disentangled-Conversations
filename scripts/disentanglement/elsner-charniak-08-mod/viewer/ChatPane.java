import javax.swing.*;
import javax.swing.event.*;
import javax.swing.text.*;
import java.io.*;
import java.util.*;
import java.util.regex.*;
import java.awt.*;
import java.awt.event.*;

public class ChatPane extends JScrollPane
{
	JTextPane contents;
	StyledDocument doc;
	Pattern linePatt;
	ChangeListener tabL;

	HashMap<String, Style> nameColors;
	Color[] colors = { Color.blue, Color.red, Color.green, Color.pink,
					   Color.orange,
					   Color.cyan, Color.yellow.darker(), Color.magenta,
					   new Color(102, 51, 102),
					   new Color(134, 138, 0),
					   new Color(0, 153, 0),
					   new Color(255, 0, 51).darker(),
					   new Color(153, 255, 153),
	};
	int nextColor;

	HashMap<Integer, Style> threadColors;
//	Color[] tColors = new Color[30];
	ArrayList<Color> tColors;
	int nextThreadColor;

	int latestTime;

	TreeMap<Integer, Line> lineBegins;
	TreeMap<Integer, TreeMap<Integer, Line>> threads;

	int nextThread = 0;
	int cLineBegin = -1;
	int cLineEnd = -1;

	ThreadWatcher[] watchers;

	public ChatPane()
	{
		super();

		tColors = new ArrayList<Color>();
		int gap = 64;
		for(int r=0; r<255; r += gap)
		{
			for(int g=0; g<255; g+=gap)
			{
				for(int b=0; b<255; b+= gap)
				{
					if(r + g + b > 450)
					{
						continue;
					}
					tColors.add(new Color(r, g, b, 180));
				}
			}
		}
		Collections.shuffle(tColors, new Random(0));

		setMaximumSize(new Dimension(1000, 1500));

		contents = new JTextPane();
		contents.setEditable(false);
		contents.setHighlighter(null);

		//setSelectedTextColor(null);
		//setSelectionColor(Color.white);

		contents.addCaretListener(new CaretHandler());
		contents.setMaximumSize(new Dimension(30, 30));
		doc = contents.getStyledDocument();
		setViewportView(contents);

		Style style = contents.addStyle("red", null);
		StyleConstants.setForeground(style, Color.red);

		style = contents.addStyle("redbold", null);
		StyleConstants.setForeground(style, Color.red);
		StyleConstants.setBold(style, true);

		style = contents.addStyle("graybg", null);
		StyleConstants.setBackground(style, upAlpha(Color.lightGray));

		style = contents.addStyle("highlight", null);
		StyleConstants.setBackground(style, upAlpha(Color.yellow));

		style = contents.addStyle("nobg", null);
		StyleConstants.setBackground(style, Color.white);

		linePatt = 
			Pattern.compile("(?:(T-?\\d+) )?(\\d+) (\\S+) (\\*|:) (.*)");

		nameColors = new HashMap<String, Style>();
		nextColor = 0;

		threadColors = new HashMap<Integer, Style>();
		nextThreadColor = 6;
		threadColors.put(Line.SYS_THREAD, contents.getStyle("graybg"));
		threadColors.put(Line.NO_THREAD, contents.getStyle("nobg"));

// 		for(int i=0; i<tColors.length; i++)
// 		{
// 			tColors[i] = upAlpha(tColors[i]);
// 		}

		latestTime = 0;

		lineBegins = new TreeMap<Integer, Line>();

// 		for(int i=0; i<=4; i++)
// 		{
// 			contents.getInputMap().put(KeyStroke.getKeyStroke("typed "+i), 
// 									   "tid"+i);
// 			contents.getActionMap().put("tid"+i, new TIDAction(i));
// 		}

		contents.getInputMap().put(KeyStroke.getKeyStroke("typed n"), 
								   "new");
		contents.getActionMap().put("new", new NewTAction());

// 		contents.getInputMap().put(KeyStroke.getKeyStroke("typed r"), 
// 								   "reselect");
// 		contents.getActionMap().put("reselect", new ReselectAction());

		contents.getInputMap().put(KeyStroke.getKeyStroke("typed u"), 
								   "clear");
		contents.getActionMap().put("clear", new TIDAction(0));

		threads = new TreeMap<Integer, TreeMap<Integer, Line> >();
	}

	public Line getLine(String line, int ctr)
	{
		Matcher m = linePatt.matcher(line);

		if(!m.matches())
		{
			throw new RuntimeException("Bad line:"+line);
		}

		String threadID = m.group(1);
		String time = m.group(2);
		String name = m.group(3);
		String commentMark = m.group(4);
		String rest = m.group(5);

// 		System.out.println("T"+threadID+" time "+time+" name "+name+
// 						   " comm "+commentMark+" rest "+rest);

		int thread = Line.NO_THREAD;
		if(threadID != null)
		{
			thread = Integer.parseInt(threadID.substring(1));
		}

		int currT = Integer.parseInt(time);

		Line thisLine = new Line(currT, name, commentMark, rest, ctr, thread);

		if(thread > nextThread)
		{
			nextThread = thread;
		}

		return thisLine;
	}

	public void addLine(Line thisLine)
	{
		int beginPutText = doc.getLength();

		lineBegins.put(beginPutText, thisLine);

		thisLine.show(doc, this, doc.getLength(), latestTime);
		latestTime = thisLine.time;

		int endPutText = doc.getLength();

		if(sysMessage(thisLine.rest))
		{
			addToThread(thisLine, beginPutText, endPutText, Line.SYS_THREAD);
		}
		else if(thisLine.willBeThread != Line.NO_THREAD)
		{
			addToThread(thisLine, beginPutText, endPutText, 
						thisLine.willBeThread);
		}
	}

	public void setBounds(int x, int y, int w, int h)
	{
		if(w > getMaximumSize().width)
		{
			w = getMaximumSize().width;
		}
		super.setBounds(x, y, w, h);
	}

	public boolean sysMessage(String message)
	{
		return message.startsWith(" entered the room") ||
			message.startsWith(" left the room") ||
			message.startsWith(" mode (") ||
			message.startsWith(" is now known as");
	}

	public void removeFromThread(Line line)
	{
		if(line.thread == Line.NO_THREAD)
		{
			return;
		}

		TreeMap<Integer, Line> tMap = threads.get(line.thread);
		tMap.remove(line.index);

		for(int w = 0; w < watchers.length; w++)
		{
			if(watchers[w].watching == line.thread)
			{
				watchers[w].remove(line);
				break;
			}
		}
	}

	public void addToThread(Line line, int begin, int end, int thread)
	{
		if(line.thread == Line.SYS_THREAD)
		{
			return;
		}

		removeFromThread(line);

		line.thread = thread;
		TreeMap<Integer, Line> tMap = threads.get(thread);
		if(tMap == null)
		{
			tMap = new TreeMap<Integer, Line>();
			threads.put(thread, tMap);
		}
		tMap.put(line.index, line);

		doc.setCharacterAttributes(begin, end-begin, 
								   getThreadColor(thread), false);

		watchThread(thread, line);
	}

	public void watchThread(int thread, Line line)
	{
		if(thread == Line.NO_THREAD || thread == Line.SYS_THREAD)
		{
			return;
		}

		boolean wasWatched = false;
		int early = Integer.MAX_VALUE;
		int earlyW = 0;
		for(int w = 0; w < watchers.length; w++)
		{
			if(watchers[w].timestamp <= early)
			{
				early = watchers[w].timestamp;
				earlyW = w;
			}

			if(watchers[w].watching == thread)
			{
				if(line != null)
				{
					watchers[w].add(line);
				}
				wasWatched = true;
				break;
			}

			if(watchers[w].watching == Line.NO_THREAD)
			{
				wasWatched = true;

				watchers[w].watch(thread);
				if(line != null)
				{
					watchers[w].add(line);
				}
				break;
			}
		}

		if(!wasWatched)
		{
			watchers[earlyW].watch(thread);
			watchers[earlyW].loadAll();
		}
	}

	public Style getNextColor()
	{
		Style style = contents.addStyle(null, null);
		StyleConstants.setForeground(style, colors[nextColor++]);
		StyleConstants.setBold(style, true);

		if(nextColor == colors.length)
		{
			nextColor = 0;
		}

		return style;
	}

	public Style getThreadColor(int thread)
	{
		if(threadColors.containsKey(thread))
		{
			return threadColors.get(thread);
		}

		Style style = contents.addStyle(null, null);
		StyleConstants.setBackground(style, tColors.get(nextThreadColor++));

		if(nextThreadColor == tColors.size())
		{
			nextThreadColor = 0;
		}

		threadColors.put(thread, style);

		return style;
	}

	public Color upAlpha(Color c)
	{
		return new Color(c.getRed(), c.getGreen(), c.getBlue(), 150);
	}

	public boolean unlabeled()
	{
		for(Map.Entry<Integer, Line> entry : lineBegins.entrySet())
		{
			if(entry.getValue().thread == 0)
			{
				contents.setCaretPosition(entry.getKey()+1);
				return true;
			}
		}

		return false;
	}

	class CaretHandler implements CaretListener
	{
		public void caretUpdate(CaretEvent e)
		{
			if(cLineBegin != -1)
			{
				doc.setCharacterAttributes(
					cLineBegin, cLineEnd-cLineBegin,
					threadColors.get(lineBegins.get(cLineBegin).thread), 
					false);
			}

			int point = e.getDot();

			SortedMap<Integer, Line> head = lineBegins.headMap(point+1);
			int begin = head.lastKey();
			
			int tailStart = point;
			if(begin == point)
			{
				tailStart++;
			}

			SortedMap<Integer, Line> tail = lineBegins.tailMap(tailStart);
			
			int end;
			if(tail.size() > 0)
			{
				end = tail.firstKey();
			}
			else
			{
				end = doc.getLength();
			}

			cLineBegin = begin;
			cLineEnd = end;

			doc.setCharacterAttributes(begin, end-begin,
									   contents.getStyle("highlight"), false);

			PointerInfo minfo = MouseInfo.getPointerInfo();
			Point loc = minfo.getLocation();
			Point myloc = contents.getLocationOnScreen();
			Point wloc = watchers[0].getLocationOnScreen();
			boolean inWatcher = false;
			if(contents.contains(loc.x - myloc.x, loc.y - myloc.y))
			{
				inWatcher = false;
			}
			else if(watchers[0].contains(loc.x - wloc.x, loc.y - wloc.y))
			{
// 				System.out.println("In the watcher!");
// 				System.out.println(loc);
// 				System.out.println(watchers[0].getBounds());

				inWatcher = true;
			}
			else
			{
// 				System.out.println("Mouse outside!");
// 				System.out.println(loc);
// 				System.out.println(watchers[0].getBounds());
				return;
			}

			if(e.getDot() == e.getMark())
			{
				//System.out.println("No selecting here!");
				watchThread(lineBegins.get(cLineBegin).thread, null);
			}
			else
			{
				//System.out.println("Selecting!");
				//this is disgustingly hackish but hey it's only 9:30 yet!

				int mark = e.getMark();

				SortedMap<Integer, Line> mhead = lineBegins.headMap(mark+1);
				int mbegin = mhead.lastKey();
			
				int mtailStart = mark;
				if(mbegin == mark)
				{
					mtailStart++;
				}

				SortedMap<Integer, Line> mtail = 
					lineBegins.tailMap(mtailStart);
			
				int mend;
				if(mtail.size() > 0)
				{
					mend = mtail.firstKey();
				}
				else
				{
					mend = doc.getLength();
				}

				if(!inWatcher)
				{
					if(lineBegins.get(cLineBegin).thread == Line.SYS_THREAD)
					{
						return;
					}
					addToThread(lineBegins.get(mbegin), mbegin, mend, 
								lineBegins.get(cLineBegin).thread);
				}
				else
				{
					addToThread(lineBegins.get(mbegin), mbegin, mend, 
								watchers[0].watching);
				}
			}				
		}
	}

	AbstractAction getclearaction()
	{
		return new TIDAction(0);
	}

	class TIDAction extends AbstractAction
	{
		int thread;

		public TIDAction(int tid)
		{
			thread = tid;
		}

		public void actionPerformed(ActionEvent e)
		{
			int addTo = thread;
			if(addTo != 0)
			{
				addTo = watchers[addTo-1].watching;
			}

			addToThread(lineBegins.get(cLineBegin), cLineBegin, cLineEnd, 
						addTo);
			try
			{
				contents.setCaretPosition(cLineEnd+1);
			}
			catch(IllegalArgumentException ex)
			{
			}
		}
	}

	AbstractAction getnewaction()
	{
		return new NewTAction();
	}

	class NewTAction extends AbstractAction
	{
		public NewTAction()
		{
		}

		public void actionPerformed(ActionEvent e)
		{
			Line theLine = lineBegins.get(cLineBegin);
			if(theLine.thread != Line.SYS_THREAD)
			{
				nextThread++;
				addToThread(theLine, cLineBegin, cLineEnd, nextThread);
			}
			try
			{
				contents.setCaretPosition(cLineEnd+1);
			}
			catch(IllegalArgumentException ex)
			{
			}
		}
	}

	class ReselectAction extends AbstractAction
	{
		public ReselectAction()
		{
		}

		public void actionPerformed(ActionEvent e)
		{
			int thread = lineBegins.get(cLineBegin).thread;
			watchThread(thread, null);
		}
	}
}
