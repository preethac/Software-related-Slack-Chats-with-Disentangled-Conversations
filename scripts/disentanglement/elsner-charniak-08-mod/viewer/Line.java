import javax.swing.*;
import javax.swing.text.*;
import java.io.*;
import java.util.*;
import java.util.regex.*;
import java.awt.*;

public class Line
{
	int thread;
	int time;
	String name;
	boolean comment;
	String rest;

	int index;

	int willBeThread;

	static int SYS_THREAD = -1;
	static int NO_THREAD = 0;

	public Line(int t, String n, String c,
				String r, int ind, int wbt)
	{
		thread = NO_THREAD;
		time = t;
		name = n;
		comment = c.equals(":");
		rest = r;
		index = ind;

		willBeThread = wbt;
	}

	public void write(PrintWriter wr)
	{
		wr.print("T"+thread+" ");

		wr.print(time+" ");

		wr.print(name+" ");

		wr.print( comment ? ":" : "*");
		wr.print(" ");

		wr.println(rest);
	}

	public Position show(Document doc, ChatPane chat, int offset, int prevT)
	{
		int deltaT = time - prevT;
		try
		{
			Style timeColor = null;
			if(deltaT > 60)
			{
				timeColor = chat.contents.getStyle("redbold");
			}
			else if(deltaT > 20)
			{
				timeColor = chat.contents.getStyle("red");
			}
			doc.insertString(offset, deltaT+"\t", timeColor);

			Position p = doc.createPosition(offset + 
											new String(deltaT+"\t").length());

			Style color = chat.nameColors.get(name);
			if(color == null)
			{
				color = chat.getNextColor();
				chat.nameColors.put(name, color);
			}
			doc.insertString(p.getOffset(), name, color);

			if(comment)
			{
				doc.insertString(p.getOffset(), ":\t", null);
			}

			doc.insertString(p.getOffset(), rest, null);
			doc.insertString(p.getOffset(), "\n", null);

			return p;
		}
		catch(Exception e)
		{
			e.printStackTrace();
		}
		return null;
	}

	void reshowTime(Document doc, ChatPane chat, int offset, int prevT)
	{
		int deltaT = time - prevT;

		try
		{
			int end = offset;
			while(!doc.getText(end, 1).equals("\t"))
			{
				end++;
			}
//			System.out.println("removing "+offset+" "+end);
			doc.remove(offset, end-offset);
			Style timeColor = null;
			if(deltaT > 60)
			{
				timeColor = chat.contents.getStyle("redbold");
			}
			else if(deltaT > 20)
			{
				timeColor = chat.contents.getStyle("red");
			}
			doc.insertString(offset, deltaT+"", timeColor);
		}
		catch(BadLocationException e)
		{
			System.out.println("bad "+e.offsetRequested());
			e.printStackTrace();
		}
	}
}
