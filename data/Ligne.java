package bus;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

public class Ligne {

	Map<String, List<String>> dic = new HashMap<>();
	private String[] slited_content;

	public Ligne(String fileName) {
		try {
			Path filePath = Path.of(fileName);
			String content = Files.readString(filePath);
			this.slited_content = content.split("\n\n");
		}catch(IOException e) {
			e.printStackTrace();
		}
	}

	private Map dates2dic(String dates) {
		Map<String, List<String>> dic = new HashMap<>();
		String[] splitted_dates = dates.split("\n");

		//System.out.println(splitted_dates);

		for(String stop_dates : splitted_dates) {
			String[] tmp = stop_dates.split(" ");
			String key = tmp[0];
			List<String> values = new ArrayList<String>(Arrays.asList(tmp));
			dic.put(key, values);
		}
		return dic;
	}

	public String regular_path() {
		return slited_content[0];
	}

	public Map regular_date_go() {
		return dates2dic(slited_content[1]);
	}

	public Map regular_date_back(){
		return dates2dic(slited_content[2]);
	}

	public String we_holidays_path(){
		return slited_content[3];
	}

	public Map we_holidays_date_go(){
		return dates2dic(slited_content[4]);
	}
	public Map we_holidays_date_back() {
		return dates2dic(slited_content[5]);
	}
}

