import javax.swing.*;
import javax.swing.text.*;
import javax.swing.border.*;
import java.io.*;
import java.util.*;
import java.util.regex.*;
import java.awt.*;

public class ThreadWatcher extends JScrollPane
{
	JTextPane contents;
	StyledDocument doc;
	ChatPane chat;
	int watching;
	int timestamp;

	static int clock = 0;

	TreeMap<Integer, Position> linePos;
	TreeMap<Integer, Line> lines;

	public ThreadWatcher(ChatPane c)
	{
		super();

		chat = c;

//  		setMaximumSize(new Dimension(1500, 1000));
//  		setPreferredSize(new Dimension(1500, 1000));

//		setMaximumSize(new Dimension(1000, 1000));
//		setPreferredSize(new Dimension(1000, 1000));

		contents = new JTextPane();
		contents.setEditable(false);
		doc = contents.getStyledDocument();

		setViewportView(contents);

		contents.setCaretPosition(doc.getLength() );

		watching = Line.NO_THREAD;

		linePos = new TreeMap<Integer, Position>();
		lines = new TreeMap<Integer, Line>();

		tick();
	}

	public void tick()
	{
		timestamp = clock++;
	}

	public void setBounds(int x, int y, int w, int h)
	{
		if(w > getMaximumSize().width)
		{
			w = getMaximumSize().width;
		}
		super.setBounds(x, y, w, h);
	}

	public void add(Line line)
	{
		tick();
		realAdd(line);
	}

	public void realAdd(Line line)
	{
		if(linePos.containsKey(line.index))
		{
//			System.out.println("already have\n");
			return;
		}

		lines.put(line.index, line);

		try
		{
			SortedMap<Integer, Position> head = linePos.headMap(line.index);
			if(head.size() == 0)
			{
//				System.out.println("this is "+line.index+ " with no prev");
				Position p = line.show(doc, chat, 0, 0);
				linePos.put(line.index, p);							
			}
			else
			{
				Position prevLine = head.get(head.lastKey());
// 				System.out.println("this is "+line.index+ 
// 								   " prev line is "+head.lastKey());
				int pOffset = prevLine.getOffset();
				line.show(doc, chat, prevLine.getOffset(),
						  lines.get(head.lastKey()).time);
				linePos.put(line.index,
							prevLine);
				linePos.put(head.lastKey(), doc.createPosition(pOffset));
			}

			SortedMap<Integer, Position> tail = linePos.tailMap(line.index+1);
			if(tail.size() > 0)
			{
				int nextLine = tail.firstKey();
				Line next = lines.get(nextLine);
				Position p = linePos.get(line.index);
				next.reshowTime(doc, chat, p.getOffset()+1,
								line.time);
				doc.remove(p.getOffset(), 1);
			}

			contents.setCaretPosition(doc.getLength() );
		}
		catch(Exception e)
		{
			e.printStackTrace();
		}
	}

	public void remove(Line line)
	{
		if(!linePos.containsKey(line.index))
		{
			return;
		}

		try
		{
			Position endOfPrev;
			int prevT;
			SortedMap<Integer, Position> head = linePos.headMap(line.index);
			if(head.size() == 0)
			{
//				System.out.println("this is "+line.index+ " with no prev");
				Position p = linePos.get(line.index);
				doc.remove(0, p.getOffset());
				prevT = 0;
				endOfPrev = p;
			}
			else
			{
 				Position prevLine = head.get(head.lastKey());
//  				System.out.println("this is "+line.index+ 
//  								   " prev line is "+head.lastKey());
				int pOffset = prevLine.getOffset();
				Position p = linePos.get(line.index);
				doc.remove(pOffset, p.getOffset() - pOffset);
				endOfPrev = p;
				prevT = lines.get(head.lastKey()).time;
			}
			linePos.remove(line.index);
			lines.remove(line.index);

			SortedMap<Integer, Position> tail = linePos.tailMap(line.index+1);
			if(tail.size() > 0)
			{
				int nextLine = tail.firstKey();
//				System.out.println("next line is "+nextLine);
				Line next = lines.get(nextLine);
				next.reshowTime(doc, chat, endOfPrev.getOffset()+1, prevT);
				doc.remove(endOfPrev.getOffset(), 1);
			}
		}
		catch(Exception e)
		{
			e.printStackTrace();
		}
	}

	public void loadAll()
	{
		tick();

		try
		{
			doc.remove(0, doc.getLength());
			lines.clear();
			linePos.clear();

			for(Line l : chat.threads.get(watching).values())
			{
				realAdd(l);
			}
		}
		catch(Exception e)
		{
			e.printStackTrace();
		}
	}

	public void watch(int thread)
	{
		watching = thread;
		setBorder(new LineBorder(StyleConstants.getBackground(
									 chat.threadColors.get(thread)), 5));
	}
}
