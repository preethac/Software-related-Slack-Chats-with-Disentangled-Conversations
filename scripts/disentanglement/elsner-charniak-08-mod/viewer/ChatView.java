import javax.swing.*;
import java.io.*;
import java.util.*;
import java.awt.*;
import java.awt.event.*;

public class ChatView extends JFrame
{
	JFileChooser fileChooser;
	ChatPane viewer;
	int lineCtr = 0;
	BufferedReader reader;
	JTabbedPane tabs;

	LinkedList<Line> lines;

	public ChatView(String filename)
	{
		super("Chat Viewer");
		setSize(1200, 950);
		setDefaultCloseOperation(EXIT_ON_CLOSE);

		fileChooser = new JFileChooser();

		Container content = getContentPane();
		content.setLayout(new BoxLayout(content, BoxLayout.X_AXIS));

		JMenuBar mbar = new JMenuBar();
		JMenu menu = new JMenu("File");
		mbar.add(menu);
		setJMenuBar(mbar);

		viewer = new ChatPane();
		content.add(viewer);

		JMenuItem save = new JMenuItem("Save");
		menu.add(save);
		save.addActionListener(new SaveAction(this));

// 		JMenuItem readMore = new JMenuItem("Read More");
// 		menu.add(readMore);
// 		readMore.addActionListener(new ReadAction());

		menu.addSeparator();

// 		JMenuItem m = new JMenuItem("Remove from thread: 0");
// 		menu.add(m);
// 		m = new JMenuItem("Add to thread #n: n");
// 		menu.add(m);
// 		m = new JMenuItem("Add to thread in upper right: 2");
// 		menu.add(m);
// 		m = new JMenuItem("Add to thread in lower left: 3");
// 		menu.add(m);
// 		m = new JMenuItem("Add to thread in lower right: 4");
// 		menu.add(m);

// 		m = new JMenuItem("New thread: n");
// 		menu.add(m);
// 		m = new JMenuItem("Reselect an old thread: r");
// 		menu.add(m);

		ThreadWatcher watcher[] = new ThreadWatcher[1];
		for(int i=0; i<watcher.length; i++)
		{
			watcher[i] = new ThreadWatcher(viewer);
		}

//    		JPanel top = new JPanel(new BorderLayout());
//    		top.setLayout(new BoxLayout(top, BoxLayout.X_AXIS));
//  		top.add(watcher[0]);
//  		top.add(watcher[1]);
		
//  		JPanel bottom = new JPanel();
//    		bottom.setLayout(new BoxLayout(bottom, BoxLayout.X_AXIS));
//  		bottom.add(watcher[2]);
//  		bottom.add(watcher[3]);

 		JPanel rightSide = new JPanel();
 		rightSide.setLayout(new BoxLayout(rightSide, BoxLayout.Y_AXIS));
// 		tabs = new JTabbedPane(JTabbedPane.TOP, JTabbedPane.SCROLL_TAB_LAYOUT);
// 		rightSide.add(tabs);

// 		rightSide.add(top);
// 		rightSide.add(bottom);

		for(int i=0; i<watcher.length; i++)
		{
			rightSide.add(watcher[i]);
		}

		JPanel bottom = new JPanel();
		bottom.setLayout(new BoxLayout(bottom, BoxLayout.X_AXIS));

		JButton newbutton = new JButton("New Thread");
		newbutton.setMnemonic(KeyEvent.VK_N);
		newbutton.setPreferredSize(new Dimension(1000, 30));
		newbutton.addActionListener(viewer.getnewaction());
		bottom.add(newbutton);

		JButton clearbutton = new JButton("Unannotate");
		clearbutton.setMnemonic(KeyEvent.VK_U);
//		newbutton.setPreferredSize(new Dimension(1000, 30));
		clearbutton.addActionListener(viewer.getclearaction());
		bottom.add(clearbutton);

		rightSide.add(bottom);

 		content.add(rightSide);

		viewer.watchers = watcher;
//		viewer.addTabs(tabs);

		lines = new LinkedList<Line>();

		try
		{
			reader = new BufferedReader(new FileReader(filename));

			int ctr = 0;
			while(true)
			{
				if(ctr % 1000 == 0)
				{
					System.out.println(ctr);
				}

				String line = reader.readLine();
				
				if(line == null)
				{
					break;
				}

				lines.addLast(viewer.getLine(line, ctr));
				ctr++;
			}

			addMoreLines();
		}
		catch(FileNotFoundException e)
		{
			throw new RuntimeException("Can't find "+filename);
		}
		catch(IOException e)
		{
			e.printStackTrace();
		}

		setVisible(true);
	}

	public void addMoreLines()
	{
		if(lines.peek() == null)
		{
			JOptionPane.showMessageDialog(this, "No more lines.");
		}

 		int end = lineCtr + 1000;
 		for(; lineCtr < end && lines.peek() != null; lineCtr++)
		{
			viewer.addLine(lines.removeFirst());
		}
	}

	class SaveAction extends AbstractAction
	{
		Component parent;
		public SaveAction(Component p)
		{
			parent = p;
		}

		public void actionPerformed(ActionEvent e)
		{
			if(viewer.unlabeled())
			{
				JOptionPane.showMessageDialog(
					parent, "Some lines still need to be annotated.");
				return;
			}

			int ret = fileChooser.showSaveDialog(parent);
			if(ret == JFileChooser.APPROVE_OPTION)
			{
				File f = fileChooser.getSelectedFile();

				if(f.exists())
				{
					JOptionPane.showMessageDialog(parent,
						"That file exists. Pick a new name.");
					return;

// 					if(JOptionPane.showConfirmDialog(
// 						   parent, "Really overwrite "+f+"?") != 
// 					   JOptionPane.YES_OPTION)
// 					{
// 						return;
// 					}
				}

				try
				{
					PrintWriter wr = new PrintWriter(new FileWriter(f));

					for(Line l : viewer.lineBegins.values())
					{
						l.write(wr);
					}

					for(Line l : lines)
					{
						l.write(wr);
					}

					wr.close();
				}
				catch(Exception ex)
				{
					ex.printStackTrace();
				}
			}
		}
	}

	class ReadAction extends AbstractAction
	{
		public ReadAction()
		{
		}

		public void actionPerformed(ActionEvent e)
		{
			addMoreLines();
		}
	}

	public static void main(String args[])
	{
		ChatView obj = new ChatView(args[0]); //main code in constructor
	}
}
