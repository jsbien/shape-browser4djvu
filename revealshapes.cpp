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

#include <map>
#include <set>

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

// Inherited dictionary ordinals (document order)
static std::map<const JB2Dict*, int> inherited_dict_id;
static bool inherited_dicts_initialized = false;

static void
init_inherited_dictionaries(GP<DjVuDocument> doc)
{
  if (inherited_dicts_initialized)
    return;

  std::set<const JB2Dict*> seen;
  int next_id = 1; // 0 reserved for page-local

  int page_count = doc->get_pages_num();

  for (int p = 0; p < page_count; ++p)
  {
    std::cerr << "DEBUG: get_page(" << p << ")\n";

    GP<DjVuImage> img = doc->get_page(p);
    if (!img)
      continue;

    GP<JB2Image> jb2 = img->get_fgjb();
    if (!jb2)
      continue;

    GP<JB2Dict> dict = jb2->get_inherited_dict();
    if (!dict)
      continue;

    const JB2Dict* dict_ptr = dict.operator->();

    if (!seen.count(dict_ptr))
    {
      inherited_dict_id[dict_ptr] = next_id++;
      seen.insert(dict_ptr);
    }
  }

  inherited_dicts_initialized = true;
}



int compute_depth(JB2Shape *shape, JB2Image *jimg) {
    int depth = 0;
    while (shape && shape->parent >= 0) {
        shape = &jimg->get_shape(shape->parent);
        depth++;
    }
    return depth;
}


int
process_document(int page_from, int page_to, GP<DjVuDocument> doc)
{
  int page_count = doc->get_pages_num();

  for (int p = page_from; p <= page_to; ++p)
  {
    GP<DjVuImage> img = doc->get_page(p);
    if (!img)
      continue;

    GP<JB2Image> jimg = img->get_fgjb();
    if (!jimg)
      continue;

    // -------------------------------
    // 1. EXPORT SHAPES 
    // -------------------------------

    {
      int shape_count = jimg->get_shape_count();

      for (int s = 0; s < shape_count; ++s)
      {
        const JB2Shape &shape = jimg->get_shape(s);

        // collect shape metadata here
        // width, height, parent, etc.
      }
    }

    // -------------------------------
    // 2. PROCESS BLITS (ALWAYS)
    // -------------------------------
    int blit_count = jimg->get_blit_count();

    for (int b = 0; b < blit_count; ++b)
    {
     const JB2Blit *blit = jimg->get_blit(b);
     if (!blit)
       continue;

     int shape_no = blit->shapeno;
     int left     = blit->left;
     int bottom   = blit->bottom;

      // collect blit info here
    }
  }

  return EXIT_SUCCESS;
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

    const GURL::Filename::UTF8 url(filename.c_str());
    GP<DjVuDocument> doc = DjVuDocument::create_wait(url);

    init_inherited_dictionaries(doc);


    int n = doc->get_pages_num();

    int from = page_from - 1;
    int to   = (page_to < 0) ? n - 1 : page_to - 1;

    if (from < 0 || to < from || to >= n)
      throw std::runtime_error("invalid page range");

    return process_document(from, to, doc);

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
