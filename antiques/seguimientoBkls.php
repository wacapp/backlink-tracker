<?php
//$urlPageBkl   array de las urls con sus fechasde aplicacion de backlinks
                foreach($urlPageBkl as $urlpage){
                    $fechasBkls = array_column($urlpage, 'cantidad', 'fecha');
                    $i = 1;
                    $fechadesde = date('Y-m', strtotime('-1 month', strtotime($urlpage[0]['anno'].'-'.$urlpage[0]['mes'].'-01')))."-01"; 
                    $intervals = Utils::date_interval($fechadesde, $fechahasta, 'P1M');
                    $total_month = count((array)$intervals);

                    foreach($intervals as $interval){
                        $date_a   = ($i == 1) ? $fechadesde : $interval->inicio;
                        $date_b   = ($i == $total_month) ? $fechahasta : $interval->fin;
                        $month    = (new \DateTime($date_a))->format('m');
                        $month_n  = (new \DateTime($date_a))->format('n');
                        $year     = (new \DateTime($date_a))->format('Y');
                        $clicks = $ctr = $impressions = $position = $dataGscKeywordsCount = "";
                        $monthYear    = strtoupper(Utils::to_string_month((int) $month))."-".$year;
                        $hasBacklinks = false; 
                        $url_medio = ""; 
                        
                        if(array_key_exists($month_n.'-'.$year, $fechasBkls)){
                            $hasBacklinks = $fechasBkls[$month_n.'-'.$year];
                            $url_medio = $urlpage[0]['url_medio'];
                        }
                        
                        $gsc->startDate = $date_a;
                        $gsc->endDate   = $date_b;
                        $gsc->startRow  = 0;
                        $gsc->groupsFilters = array([$gsc::DIMENSION_PAGE, $urlpage[0]['url_page'], $gsc::OPERATOR_EQUALS]);
                        $dataGsc = $gsc->getData()[0];
                
                        $gsc->startDate = $date_a;
                        $gsc->endDate   = $date_b;
                        $gsc->query = true;
                        $gsc->startRow  = 0;
                        $gsc->groupsFilters = array([$gsc::DIMENSION_PAGE, $urlpage[0]['url_page'], $gsc::OPERATOR_EQUALS]);
                        $dataGscKeywords = $gsc->getData();
                        $dataGscKeywordsCount = is_array($dataGscKeywords) ? count($dataGscKeywords) : 0;

                        if(is_object($dataGsc)){
                            $clicks = $dataGsc->clicks;
                            $ctr = round($dataGsc->ctr * 100,1) . ' %';
                            $impressions = $dataGsc->impressions;
                            $position = round($dataGsc->position,1);
                        }


                        $arrayDataProvider[] =  [   'nombreCliente' => $clientes[$user_id],
                                                    'url' => $urlpage[0]['url_ga'],
                                                    'url_page' => $urlpage[0]['url_page'],
                                                    'url_medio' => $url_medio,
                                                    'clicks' => $clicks,
                                                    'ctr' => $ctr,
                                                    'impressions' => $impressions,
                                                    'position' => $position,
                                                    'month' =>  (($i == 1) ? "MES ANTES DE REALIZAR BACKLINKS " : "").$monthYear,
                                                    'keywords_all' => $dataGscKeywordsCount,
                                                    'hasBacklinks' => $hasBacklinks,
                                                ];

                        $i++;
                    }
                }
?>                