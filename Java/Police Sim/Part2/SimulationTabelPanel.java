package Part2;

import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;

import java.awt.Dimension;


public class SimulationTabelPanel extends JPanel {
	
	public SimulationTabelPanel(SimulationTableModel tableModel) {
	
		final JTable table = new JTable();
		
		table.setPreferredScrollableViewportSize(new Dimension(600, 200));
		table.setFillsViewportHeight(true);
		table.setShowHorizontalLines(false);
		table.setShowVerticalLines(false);
		table.setModel(tableModel);
		
		JScrollPane scrollPane = new JScrollPane(table);
		
		add(scrollPane);
		
	}
	
	

}
