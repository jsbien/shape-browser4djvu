s
/***
 * 
 * Exportshapes is a program that extracts shape dictionary data 
 * from a djvu file into a database.
 *
 * Copyright © 2012 -- Piotr Sikora.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 * 
 ***/

#include <iostream>
#include <exception>
#include <string>
#include <sstream>
#include <map>
#include <vector>
#include <bits/getopt_core.h>
#include <bits/getopt_core.h>

#include "DjVuDocument.h"
#include "DjVuImage.h"
#include "/usr/include/libdjvu/ddjvuapi.h"
#include "DjVmDir.h"
#include "JB2Image.h"
#include "Arrays.h"
#include "GBitmap.h"
#include "UnicodeByteStream.h"

#include <cstdlib>
#include <unistd.h>
#include <filesystem>
// Removed redefinition to avoid conflict with config.h
#include <algorithm> 

using namespace std;

typedef std::pair<int, int> IntPair;

typedef struct {
	int right, top, left, bottom;
} BoundingBox;

#include <fstream>
std::ostream* out_stream = &std::cout;
std::ofstream out_file;
char *output_file = nullptr;
bool test_run = false, poliqarp = false;

struct ShapeStats {
    int depth = 0;
    int descendants = 0;
    int siblings = 0;
    int occurrences = 0;
    int width = 0;
    int height = 0;
};

// Declare filename before usage
std::string filename;
std::map<int, ShapeStats> shape_stats;



int compute_depth(JB2Shape *shape, JB2Image *jimg) {
    int depth = 0;
    while (shape && shape->parent >= 0) {
        shape = &jimg->get_shape(shape->parent);
        depth++;
    }
    return depth;
}



int process_document(int page_from, int page_to, GP<DjVuDocument> doc) {
	const int pages = doc->get_pages_num();
	int page_start, page_limit;
	page_start = (page_from < 1) ? 0 : page_from - 1;
	if (page_to < 1 || page_to >= pages)
		page_limit = pages;
	else
		page_limit = page_to;
	if (page_limit <= page_start) {
		std::cout << "Can't process less than one page." << std::endl;
		return EXIT_FAILURE;
	}
    std::filesystem::path sorig = filename;
	std::string sorigString = sorig.string();
        sorigString.erase(std::remove_if(sorigString.begin(), sorigString.end(), [](char c) { return c == '\"'; }), sorigString.end());
	std::filesystem::path s = filename;
if (!poliqarp)
    *out_stream << "sjbz or djbz,page number,blit number,blit shapeno,shape bits columns,rows,rowsize,blit bottom, left,depth,descendants,siblings,occurrences" << endl;


	for(int page_number = page_start; page_number < page_limit; page_number++) {

		GP<DjVuImage> djvu_page = doc->get_page(page_number);

		if (!djvu_page) {
			std::cout << "Failed to get DjVuImage for page" << page_number << std::endl;
			return EXIT_FAILURE;
		} else {

			GP<DjVuFile> djvu_file = djvu_page->get_djvu_file();
			GP<JB2Image> jimg = djvu_page->get_fgjb();
			if (!djvu_file) {
			  std::cout << "Failed to get DjVUFile for page " << page_number << std::endl;
			  return EXIT_FAILURE;  // ✅ Add this
			}
			else if (!jimg) {
			  std::cout << "Failed to get JB2Image for page " << page_number << std::endl;
			  return EXIT_FAILURE;  // ✅ Add this
			}
		        else {//export shapes
				if (test_run)
					std::cout << "Processing page " << page_number << " containing " << jimg->get_shape_count() << " shapes, " << jimg->get_inherited_shape_count() << " of them inherited." << std::endl;
				GP<JB2Dict> inherited_dictionary = jimg->get_inherited_dict();
				// int inh_dict_id = -1;
				// int inh_sh_count = jimg->get_inherited_shape_count();


				string page_name = (string) djvu_file->get_url().fname();
				// int sh_count = jimg->get_shape_count();
                // Build shape hierarchy stats
                    for (int s = 0; s < jimg->get_shape_count(); ++s) {
                        JB2Shape &shape = jimg->get_shape(s);
                        if (!shape.bits) continue;

                        ShapeStats &stats = shape_stats[s];
                        stats.depth = compute_depth(&shape, jimg);
                        stats.width = shape.bits->columns();
                        stats.height = shape.bits->rows();

                        if (shape.parent >= 0) {
			  // const JB2Shape &parent = jimg->get_shape(shape.parent);
			    int parent_no = shape.parent;
			    shape_stats[parent_no].descendants++;
// Comment out siblings for now, unless you compute them manually
// shape_stats[parent_no].siblings = ???;
						}
                        }
                    }
			int blit_count = jimg->get_blit_count();
			int inh_sh_count = jimg->get_inherited_shape_count();
                        for (int i = 0; i < jimg->get_blit_count(); ++i) {
			  JB2Blit *blit = jimg->get_blit(i);
                    if (blit) {
                        shape_stats[blit->shapeno].occurrences++;
					std::cout << "Processing blits. " << std::endl;
				for (int i = 0; i < blit_count; i++) {
                    // Count shape usage
				  for (int i = 0; i < blit_count; i++) {
				    JB2Blit *blit = jimg->get_blit(i);
				    if (blit) {
				      shape_stats[blit->shapeno].occurrences++;
						JB2Shape shape = jimg->get_shape(blit->shapeno);
						if (poliqarp ) {
							//<file-name> d-<blit number>-<blit shapeno>;file:<file-name>?djvuopts=&highlight=<left>,<blit bottom>,<shape bit columns>,<rows>&page=<page number + 1>; <file-name> d-<blit number>-<blit shapeno>;
*out_stream << s.replace_extension().filename();
*out_stream << " d-" << i << "-" << blit->shapeno << ";";
*out_stream << "file:" << sorigString << "?djvuopts=&highlight=" << blit->left << "," << blit->bottom << "," << shape.bits->columns() << "," << shape.bits->rows() << "&page=" << (page_number + 1) << ";";
*out_stream << s.filename() << " d-" << i << "-" << blit->shapeno << std::endl;
						} else {
						  *out_stream << ((blit->shapeno < static_cast<unsigned int>(inh_sh_count))?"s":"d") << "," << (page_number + 1) << "," << i << "," << blit->shapeno  << "," << shape.bits->columns() << ","  << shape.bits->rows() << ","  << shape.bits->rowsize() << "," << blit->bottom << ","  << blit->left << "," << shape_stats[blit->shapeno].depth << "," << shape_stats[blit->shapeno].descendants << "," << shape_stats[blit->shapeno].siblings << "," << shape_stats[blit->shapeno].occurrences << endl;
						}
					}
				}
			}
		}
	}
	return EXIT_SUCCESS;
}
	}
}
void usage(const char *program_name);


void usage(const char *program_name) {
    std::cout << "RevealShapes version " << VERSION << std::endl;
    std::cout << "Usage: " << program_name << " [options] <input_file>" << std::endl;
    std::cout << "Options:" << std::endl;
    std::cout << "  -f <n>         Start from page number n" << std::endl;
    std::cout << "  -t <n>         Stop at page number n" << std::endl;
    std::cout << "  -T             Verbose/debug mode" << std::endl;
    std::cout << "  -p             Output links for Poliqarp indexing" << std::endl;
    std::cout << "  -l             Output only links (currently unused)" << std::endl;
    std::cout << "  -o <file>      Specify output file (default: standard output)" << std::endl;
    std::cout << "  -h             Show this help message and exit" << std::endl;
}

int main(int argc, char **argv)
{
  try {
    int c;
    int page_from = 1, page_to = -1;
    bool links_only = false;

    while ((c = getopt(argc, argv, "Tlpf:t:o:h")) != -1) {
      switch (c) {
        case 'T': test_run = true; break;
        case 'f': page_from = atoi(optarg); break;
        case 't': page_to = atoi(optarg); break;
        case 'p': poliqarp = true; break;
        case 'l': links_only = true; break;
        case 'o': output_file = optarg; break;
        case 'h':
          usage(argv[0]);
          return EXIT_SUCCESS;
        default:
          usage(argv[0]);
          return EXIT_FAILURE;
      }
    }

    if (optind >= argc)
      throw std::runtime_error("missing input filename");

    filename = argv[optind];

    if (output_file) {
      out_file.open(output_file);
      if (!out_file)
        throw std::runtime_error("cannot open output file");
      out_stream = &out_file;
    }

    GP<DjVuDocument> doc = DjVuDocument::create_wait(
        GURL(GUTF8String(filename.c_str())));

    return process_document(page_from, page_to, doc);
  }
  catch (const DJVU::GException &e) {
    e.perror();
    return EXIT_FAILURE;
  }
  catch (const std::exception &e) {
    std::cerr << e.what() << std::endl;
    return EXIT_FAILURE;
  }
}
